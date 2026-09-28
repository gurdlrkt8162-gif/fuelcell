#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from scripts import build_hydrogen_guide as b


def parse_timestamp_text(text: str) -> list[dict[str, Any]]:
    rows = [x.strip() for x in text.splitlines() if x.strip()]
    pat = re.compile(r'^\(?\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*\)?\s+(.+)$')
    pending: list[tuple[float, str]] = []
    for row in rows:
        m = pat.match(row)
        if m:
            pending.append((b.stamp_to_sec(m.group(1)), b.norm_text(m.group(2))))
    out: list[dict[str, Any]] = []
    for i, (start, text) in enumerate(pending):
        end = pending[i + 1][0] if i + 1 < len(pending) else start + max(2.0, min(12.0, len(text) / 5.0))
        b.add_seg(out, start, end, text)
    return out


def browser_probe(key: str, url: str, work: Path) -> tuple[list[dict[str, Any]], list[str]]:
    outdir = b.ensure_dir(work / "browser" / key)
    segs: list[dict[str, Any]] = []
    urls: set[str] = set()
    response_counter = 0
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium") or shutil.which("chromium-browser")

    with sync_playwright() as pw:
        launch_kw: dict[str, Any] = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if chrome:
            launch_kw["executable_path"] = chrome
        browser = pw.chromium.launch(**launch_kw)
        context = browser.new_context(viewport={"width": 1440, "height": 1800}, locale="ko-KR")
        page = context.new_page()

        def on_response(resp: Any) -> None:
            nonlocal response_counter
            try:
                urls.add(resp.url)
                ct = (resp.headers.get("content-type") or "").lower()
                resource_type = resp.request.resource_type
                if resource_type == "media" or "video" in ct or "audio" in ct or "mpegurl" in ct:
                    (outdir / "media_urls.txt").open("a", encoding="utf-8").write(resp.url + "\n")
                if any(x in ct for x in ["json", "text", "javascript"]) and response_counter < 160:
                    body = resp.text()
                    response_counter += 1
                    (outdir / f"response_{response_counter:03d}.txt").write_text(body[:2_000_000], encoding="utf-8", errors="ignore")
                    try:
                        obj = json.loads(body)
                        b.walk_json(obj, segs, urls)
                    except Exception:
                        pass
                    segs.extend(parse_timestamp_text(body))
                    for u in re.findall(r'https?:\\?/\\?/[^\"\'<>\s]+', body):
                        urls.add(u.replace("\\/", "/").replace("\\u0026", "&"))
            except Exception:
                return

        page.on("response", on_response)
        page.goto(url, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(8_000)
        for label in ["View Full Transcript", "전체 전사 보기", "Show More", "더보기"]:
            try:
                locator = page.get_by_text(label, exact=False)
                if locator.count():
                    locator.first.click(timeout=5_000)
                    page.wait_for_timeout(5_000)
            except Exception:
                pass
        try:
            page.mouse.wheel(0, 20_000)
            page.wait_for_timeout(3_000)
        except Exception:
            pass

        body_text = page.locator("body").inner_text(timeout=30_000)
        html = page.content()
        (outdir / "body.txt").write_text(body_text, encoding="utf-8", errors="ignore")
        (outdir / "page.html").write_text(html, encoding="utf-8", errors="ignore")
        page.screenshot(path=str(outdir / "page.png"), full_page=True)
        segs.extend(parse_timestamp_text(body_text))
        segs.extend(parse_timestamp_text(html))

        try:
            resources = page.evaluate("performance.getEntriesByType('resource').map(e => e.name)")
            for u in resources or []:
                urls.add(str(u))
        except Exception:
            pass
        try:
            srcs = page.eval_on_selector_all("video, audio, source", "els => els.map(e => e.currentSrc || e.src).filter(Boolean)")
            for u in srcs or []:
                urls.add(str(u))
        except Exception:
            pass
        try:
            stores = page.evaluate("() => ({local:{...localStorage}, session:{...sessionStorage}})")
            (outdir / "storage.json").write_text(json.dumps(stores, ensure_ascii=False, indent=2), encoding="utf-8")
            b.walk_json(stores, segs, urls)
        except Exception:
            pass
        browser.close()

    # Parse rendered HTML and scripts once more with the normal parser helpers.
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup((outdir / "page.html").read_text(encoding="utf-8", errors="ignore"), "lxml")
        for sc in soup.find_all("script"):
            txt = sc.string or sc.get_text() or ""
            try:
                b.walk_json(json.loads(txt), segs, urls)
            except Exception:
                pass
            segs.extend(parse_timestamp_text(txt))
    except Exception:
        pass

    uniq: dict[tuple[int, str], dict[str, Any]] = {}
    for s in segs:
        k = (int(round(float(s["start"]) * 10)), b.norm_text(s["text"]))
        if k[1] and (k not in uniq or float(s["end"]) > float(uniq[k]["end"])):
            uniq[k] = {"start": float(s["start"]), "end": float(s["end"]), "text": k[1]}
    result = sorted(uniq.values(), key=lambda z: (z["start"], z["end"]))
    (outdir / "urls.txt").write_text("\n".join(sorted(urls)), encoding="utf-8")
    (outdir / "segments.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    b.log(f"{key}: browser segments={len(result)}, urls={len(urls)}, coverage={b.transcript_coverage(result, 1):.1f}s")
    return result, sorted(urls)


def download_media_any(url: str, dest: Path) -> None:
    low = url.lower()
    if ".m3u8" in low or "mpegurl" in low:
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", url, "-vn", "-ac", "1", "-ar", "16000", str(dest)], check=True, timeout=1800)
    else:
        b.download(url, dest)


def patched_get_transcript(key: str, spec: dict[str, Any], work: Path, outdir: Path, model_name: str) -> list[dict[str, Any]]:
    segs0, urls0 = b.parse_share_page(spec["share_url"], work / f"{key}.html")
    segs1, urls1 = browser_probe(key, spec["share_url"], work)
    merged = segs0 + segs1
    uniq: dict[tuple[int, str], dict[str, Any]] = {}
    for s in merged:
        k = (int(round(float(s["start"]) * 10)), b.norm_text(s["text"]))
        if k[1] and (k not in uniq or float(s["end"]) > float(uniq[k]["end"])):
            uniq[k] = {"start": float(s["start"]), "end": float(s["end"]), "text": k[1]}
    segs = sorted(uniq.values(), key=lambda z: (z["start"], z["end"]))
    coverage = b.transcript_coverage(segs, float(spec["duration"]))
    b.log(f"{key}: combined transcript segments={len(segs)}, coverage={coverage:.3f}")

    if coverage < 0.90:
        media = b.pick_media(urls0 + urls1)
        if media:
            media_path = work / f"{key}.media"
            download_media_any(media, media_path)
            from faster_whisper import WhisperModel
            threads = max(2, os.cpu_count() or 2)
            model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=threads, num_workers=1)
            iterator, info = model.transcribe(str(media_path), language="ko", beam_size=5, vad_filter=True,
                                              vad_parameters={"min_silence_duration_ms":350},
                                              initial_prompt=b.PROMPT, condition_on_previous_text=True)
            segs = []
            for s in iterator:
                b.add_seg(segs, s.start, s.end, s.text)
            coverage = b.transcript_coverage(segs, float(spec["duration"]))
            b.log(f"{key}: direct-media ASR segments={len(segs)}, coverage={coverage:.3f}")

    if coverage < 0.90:
        raise RuntimeError(f"{key}: full transcript/media unavailable after browser probe (coverage={coverage:.3f})")

    (outdir / f"{key}.json").write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    with (outdir / f"{key}.txt").open("w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"[{b.sec_to_stamp(s['start'])}-{b.sec_to_stamp(s['end'])}] {s['text']}\n")
    return segs


if __name__ == "__main__":
    b.get_transcript = patched_get_transcript
    b.main()
