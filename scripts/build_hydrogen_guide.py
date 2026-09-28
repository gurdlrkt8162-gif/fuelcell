#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_lib
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote

import fitz
import requests
from bs4 import BeautifulSoup

PROMPT = (
    "수소에너지 실험, 전기화학, Linear Sweep Voltammetry LSV, "
    "Electrochemical Impedance Spectroscopy EIS, Nyquist, Bode, "
    "Randles-Sevcik, Nernst, potentiostatic, galvanostatic, current interrupt, "
    "PEMFC, Nafion, catalyst layer, gas diffusion layer GDL, microporous layer MPL, "
    "bipolar plate, electro-osmotic drag, back diffusion, Sabatier, test station."
)

TERM_FIX = {
    "linnial sweet boltarmatry": "Linear Sweep Voltammetry",
    "리니얼 스윕 볼타메트리": "Linear Sweep Voltammetry",
    "선형 주사 전입법": "선형주사전위법",
    "선형주사 전입법": "선형주사전위법",
    "전기화학 인피던스 분권법": "전기화학 임피던스 분광법",
    "전기화학 임피던스 분권법": "전기화학 임피던스 분광법",
    "PAMFC": "PEMFC", "Pamfc": "PEMFC", "PFC": "PEMFC",
    "Fuel Stell": "Fuel Cell", "Mambrane": "membrane", "Catalist": "catalyst",
    "Gasdiffersion Layer": "gas diffusion layer", "Bipolar Plaate": "bipolar plate",
    "Bipularprate": "bipolar plate", "전자 및 10 전도": "전자 및 열전도",
    "네피온": "Nafion", "나피온": "Nafion", "사바티에": "Sabatier",
    "나이퀴스트": "Nyquist", "보드 플롯": "Bode plot", "와버그": "Warburg",
    "래들스": "Randles", "그래트후스": "Grotthuss", "그로투스": "Grotthuss",
}

# Visual slide windows verified in the two PEMFC videos.
PEMFC_260914 = {
    1:(0,47), 2:(47,128), 3:(128,218), 4:(218,277), 5:(277,348), 6:(348,399),
    7:(399,448), 8:(448,516), 9:(516,578), 10:(578,669), 11:(669,707),
    12:(707,757), 13:(757,807), 14:(807,897), 15:(897,1028), 16:(1028,1030),
    17:(1030,1032), 22:(1032,1034), 23:(1034,1044), 24:(1044,1048),
    25:(1048,1052), 26:(1052,1058), 27:(1058,1067), 28:(1067,1076),
    29:(1076,1080), 30:(1080,1084.55),
}
PEMFC_260916 = {
    1:(0,8), 2:(8,10), 3:(10,18), 4:(18,20), 5:(20,28), 6:(28,30),
    7:(30,38), 8:(38,40), 9:(40,48), 10:(48,50), 11:(50,58), 12:(58,60),
    13:(60,68), 14:(68,70), 15:(70,76), 16:(76,136), 17:(136,186),
    18:(186,246), 19:(246,320), 20:(320,390), 21:(390,470), 22:(470,512),
    23:(512,538), 24:(538,562), 25:(562,604), 26:(604,636), 27:(636,670),
    28:(670,736), 29:(736,808), 30:(808,946.42),
}


def log(msg: str) -> None:
    print(msg, flush=True)


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def download(url: str, dest: Path) -> None:
    log(f"download: {dest.name}")
    with requests.get(url, stream=True, timeout=(30, 600), headers={"User-Agent":"Mozilla/5.0"}) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
    if dest.stat().st_size < 1024:
        raise RuntimeError(f"download too small: {dest}")


def sec_to_stamp(x: float) -> str:
    x = max(0, int(round(x)))
    h, rem = divmod(x, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def stamp_to_sec(s: str) -> float:
    vals = [float(v) for v in s.strip().split(":")]
    if len(vals) == 2:
        return vals[0] * 60 + vals[1]
    return vals[0] * 3600 + vals[1] * 60 + vals[2]


def norm_text(s: Any) -> str:
    s = unicodedata.normalize("NFKC", html_lib.unescape(str(s)))
    s = s.replace("\x00", " ").replace("�", " ")
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in TERM_FIX.items():
        s = s.replace(a, b)
    s = re.sub(r"\b(어|음|그|저기|뭐냐면)\b[, ]*", "", s)
    s = re.sub(r"\s+([,.?!])", r"\1", s)
    return s.strip()


def add_seg(out: list[dict[str, Any]], start: Any, end: Any, text: Any) -> None:
    try:
        a, b = float(start), float(end)
    except Exception:
        return
    t = norm_text(text)
    if t and b > a:
        out.append({"start": a, "end": b, "text": t})


def walk_json(obj: Any, out: list[dict[str, Any]], urls: set[str]) -> None:
    if isinstance(obj, dict):
        low = {str(k).lower(): v for k, v in obj.items()}
        if "start" in low and "end" in low and "text" in low:
            add_seg(out, low["start"], low["end"], low["text"])
        for k, v in obj.items():
            if isinstance(v, str) and "url" in str(k).lower() and v.startswith("http"):
                urls.add(v)
            walk_json(v, out, urls)
    elif isinstance(obj, list):
        for v in obj:
            walk_json(v, out, urls)
    elif isinstance(obj, str) and obj.startswith("http"):
        urls.add(obj)


def parse_share_page(url: str, debug_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    log(f"fetch share page: {url}")
    r = requests.get(url, timeout=90, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    raw = r.text
    debug_path.write_text(raw, encoding="utf-8")
    soup = BeautifulSoup(raw, "lxml")
    segs: list[dict[str, Any]] = []
    urls: set[str] = set()

    for sc in soup.find_all("script"):
        body = sc.string or sc.get_text() or ""
        if not body.strip():
            continue
        try:
            walk_json(json.loads(body), segs, urls)
        except Exception:
            pass
        # Next/RSC data frequently stores JSON-like escaped transcript entries.
        for m in re.finditer(r'"start"\s*:\s*([0-9.]+).*?"end"\s*:\s*([0-9.]+).*?"text"\s*:\s*"((?:\\.|[^"\\])*)"', body, re.S):
            try:
                txt = json.loads('"' + m.group(3) + '"')
            except Exception:
                txt = m.group(3)
            add_seg(segs, m.group(1), m.group(2), txt)
        for u in re.findall(r"https?:\\?/\\?/[^\"'<>\s]+", body):
            urls.add(html_lib.unescape(u.replace("\\/", "/").replace("\\u0026", "&")))

    # Parse human-readable timestamp rows such as '(5:14) sentence'.
    rows = [x.strip() for x in soup.get_text("\n").splitlines() if x.strip()]
    timed = re.compile(r'^\((\d{1,2}:\d{2}(?::\d{2})?)\)\s*(.+)$')
    pending: list[tuple[float, str]] = []
    for row in rows:
        m = timed.match(row)
        if m:
            pending.append((stamp_to_sec(m.group(1)), norm_text(m.group(2))))
    for i, (a, t) in enumerate(pending):
        b = pending[i + 1][0] if i + 1 < len(pending) else a + max(2, min(12, len(t) / 5))
        add_seg(segs, a, b, t)

    for tag in soup.find_all(["video", "audio", "source"]):
        src = tag.get("src")
        if src:
            urls.add(src)

    uniq: dict[tuple[int, str], dict[str, Any]] = {}
    for s in segs:
        key = (int(round(s["start"] * 10)), s["text"])
        if key not in uniq or s["end"] > uniq[key]["end"]:
            uniq[key] = s
    return sorted(uniq.values(), key=lambda z: (z["start"], z["end"])), sorted(urls)


def media_candidates(raw_urls: Iterable[str]) -> list[str]:
    out: list[str] = []
    for u in raw_urls:
        u = html_lib.unescape(unquote(u)).replace("\\/", "/")
        if not u.startswith("http"):
            continue
        low = u.lower()
        if any(x in low for x in [".mp4", ".m4a", ".mp3", ".wav", ".webm", ".mov", ".m3u8", "download", "media", "storage", "blob"]):
            out.append(u)
    return list(dict.fromkeys(out))


def pick_media(urls: list[str]) -> str | None:
    for u in media_candidates(urls):
        try:
            rr = requests.get(u, headers={"Range":"bytes=0-2047", "User-Agent":"Mozilla/5.0"}, timeout=25, allow_redirects=True)
            ct = rr.headers.get("content-type", "").lower()
            if rr.status_code in (200, 206) and ("video" in ct or "audio" in ct or any(e in u.lower() for e in [".mp4", ".m4a", ".mp3", ".wav", ".webm", ".mov"])):
                log(f"media URL found: {u[:140]}")
                return u
        except Exception:
            continue
    return None


def transcribe_media(media_url: str, media_path: Path, model_name: str) -> list[dict[str, Any]]:
    download(media_url, media_path)
    from faster_whisper import WhisperModel
    threads = max(2, os.cpu_count() or 2)
    log(f"load Whisper model {model_name}, threads={threads}")
    model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=threads, num_workers=1)
    segments, info = model.transcribe(
        str(media_path), language="ko", beam_size=5, vad_filter=True,
        vad_parameters={"min_silence_duration_ms":350}, initial_prompt=PROMPT,
        condition_on_previous_text=True,
    )
    out: list[dict[str, Any]] = []
    for s in segments:
        add_seg(out, s.start, s.end, s.text)
    log(f"ASR complete: {len(out)} segments, lang={getattr(info, 'language', None)}")
    return out


def transcript_coverage(segs: list[dict[str, Any]], duration: float) -> float:
    return max((s["end"] for s in segs), default=0.0) / duration if duration else 0.0


def get_transcript(key: str, spec: dict[str, Any], work: Path, outdir: Path, model_name: str) -> list[dict[str, Any]]:
    segs, urls = parse_share_page(spec["share_url"], work / f"{key}.html")
    cov = transcript_coverage(segs, spec["duration"])
    log(f"{key}: share segments={len(segs)}, coverage={cov:.3f}")
    if cov < 0.90:
        media = pick_media(urls)
        if not media:
            raw = (work / f"{key}.html").read_text(encoding="utf-8", errors="ignore")
            media = pick_media(re.findall(r"https?[^\"'<>\s\\]+", raw))
        if not media:
            raise RuntimeError(f"{key}: full transcript unavailable and no media URL found (coverage={cov:.3f})")
        segs = transcribe_media(media, work / f"{key}.media", model_name)
        cov = transcript_coverage(segs, spec["duration"])
    if cov < 0.90:
        raise RuntimeError(f"{key}: transcript coverage too low after ASR: {cov:.3f}")
    (outdir / f"{key}.json").write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    with (outdir / f"{key}.txt").open("w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"[{sec_to_stamp(s['start'])}-{sec_to_stamp(s['end'])}] {s['text']}\n")
    return segs


def extract_interval(text: str) -> tuple[float, float] | None:
    patterns = [
        r'\[(?:약\s*)?(\d{1,2}:\d{2}(?::\d{2})?)\s*[–—-]\s*(\d{1,2}:\d{2}(?::\d{2})?)\]',
        r'영상\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[–—-]\s*(\d{1,2}:\d{2}(?::\d{2})?)',
        r'구간\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[–—-]\s*(\d{1,2}:\d{2}(?::\d{2})?)',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return stamp_to_sec(m.group(1)), stamp_to_sec(m.group(2))
    return None


def identify_page(text: str) -> tuple[str, int] | None:
    m = re.search(r'기초\s*전기화학\s*분석\s*[·\-]\s*(?:강의자료\s*)?p\.?\s*(\d+)', text, re.I)
    if m:
        return "electro", int(m.group(1))
    if "PEMFC" in text or "양성자교환막" in text:
        m = re.search(r'(?:강의자료\s*)?p\.?\s*(\d+)', text, re.I)
        if m and 1 <= int(m.group(1)) <= 30:
            return "pemfc", int(m.group(1))
    return None


def clean_existing(s: str) -> str:
    s = norm_text(s)
    s = re.sub(r'\b\d{3}\b', '', s)
    s = s.replace("를 설명한다.를 설명한다.", "를 설명한다.")
    s = s.replace("의 인과관계를 앞뒤 페이지와 연결한다.", "앞뒤 개념과의 인과관계를 연결한다.")
    s = re.sub(r'실제 분석에서는 입력.*?확인한다\.?', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def between(text: str, starts: list[str], ends: list[str]) -> str:
    pos = -1
    for st in starts:
        m = re.search(st, text, re.I)
        if m:
            pos = m.end()
            break
    if pos < 0:
        return ""
    stop = len(text)
    for en in ends:
        m = re.search(en, text[pos:], re.I)
        if m:
            stop = min(stop, pos + m.start())
    return clean_existing(text[pos:stop])


def existing_sections(text: str) -> dict[str, str]:
    return {
        "easy": between(text, [r'\b2\s*쉽게 이해하기\b', r'쉽고 자세한 설명'], [r'\b3\s', r'교수 설명', r'관련[·\s]심화']),
        "deep": between(text, [r'관련[·\s]심화(?: 개념)?', r'관련 개념 · 심화 · 연구 연결'], [r'교수 설명', r'핵심 정리', r'추가 학습']),
        "research": between(text, [r'추가 학습[·\s]연구 동향', r'연구 연결'], [r'핵심 정리', r'핵심\s']),
        "core": between(text, [r'핵심 정리\s*및 요약', r'핵심 정리'], [r'$']),
        "slide": between(text, [r'1\s*PPT 내용 해석'], [r'\b2\s*쉽게 이해하기']),
    }


def overlap_segments(segs: list[dict[str, Any]], start: float, end: float) -> list[dict[str, Any]]:
    return [s for s in segs if s["end"] > start and s["start"] < end]


def dedup_sentences(text: str) -> str:
    parts = re.split(r'(?<=[.!?다요])\s+', norm_text(text))
    seen: set[str] = set()
    out: list[str] = []
    for p in parts:
        p = p.strip(" •")
        if len(p) < 2:
            continue
        key = re.sub(r'\W+', '', p)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return " ".join(out)


def combine_speech(groups: list[tuple[str, float, float, list[dict[str, Any]]]]) -> tuple[str, str, int]:
    blocks: list[str] = []
    labels: list[str] = []
    total = 0
    for label, a, b, segs in groups:
        ss = overlap_segments(segs, a, b)
        if not ss:
            continue
        labels.append(f"{label} {sec_to_stamp(a)}-{sec_to_stamp(b)}")
        tx = dedup_sentences(" ".join(x["text"] for x in ss))
        total += len(tx)
        if tx:
            blocks.append(tx)
    return "\n\n".join(blocks), "; ".join(labels), total


def short_sentences(text: str, max_chars: int) -> str:
    text = clean_existing(text)
    if len(text) <= max_chars:
        return text
    out: list[str] = []
    count = 0
    for s in re.split(r'(?<=[.!?다요])\s+', text):
        if count + len(s) > max_chars and out:
            break
        out.append(s)
        count += len(s) + 1
    return " ".join(out).strip()


def make_summary(core: str, speech: str, easy: str, deep: str) -> str:
    candidates: list[str] = []
    for src in [core, easy, speech, deep]:
        for s in re.split(r'(?<=[.!?다요])\s+', clean_existing(src)):
            s = s.strip(" •")
            if len(s) > 15 and all(re.sub(r'\W+', '', s) != re.sub(r'\W+', '', x) for x in candidates):
                candidates.append(s)
            if len(candidates) >= 4:
                break
        if len(candidates) >= 4:
            break
    return short_sentences(" ".join(candidates), 650)


def font_paths() -> tuple[str, str]:
    regs = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    bolds = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]
    reg = next((x for x in regs if Path(x).exists()), None)
    bold = next((x for x in bolds if Path(x).exists()), reg)
    if not reg:
        raise RuntimeError("Korean font not found")
    return reg, bold


def fit_text(page: fitz.Page, rect: fitz.Rect, text: str, fontname: str, fontfile: str,
             start_size: float, min_size: float, color: tuple[float, float, float], lineheight: float = 1.25,
             align: int = fitz.TEXT_ALIGN_LEFT) -> float:
    size = start_size
    while size >= min_size:
        rc = page.insert_textbox(rect, text, fontname=fontname, fontfile=fontfile, fontsize=size,
                                 color=color, lineheight=lineheight, align=align, overlay=True)
        if rc >= 0:
            return size
        size -= 0.25
    reduced = short_sentences(text, max(300, int(len(text) * 0.82)))
    rc = page.insert_textbox(rect, reduced, fontname=fontname, fontfile=fontfile, fontsize=min_size,
                             color=color, lineheight=1.18, align=align, overlay=True)
    if rc < 0:
        raise RuntimeError(f"text overflow: {text[:100]}")
    return min_size


def draw_panel(page: fitz.Page, speech: str, time_label: str, sec: dict[str, str], summary: str,
               reg: str, bold: str) -> None:
    W, H = page.rect.width, page.rect.height
    panel = fitz.Rect(W * 0.535, H * 0.165, W * 0.985, H * 0.865)
    bottom = fitz.Rect(W * 0.018, H * 0.878, W * 0.985, H * 0.982)
    page.add_redact_annot(panel, fill=(0.94, 0.985, 0.985))
    page.add_redact_annot(bottom, fill=(0.91, 0.95, 0.98))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    page.draw_rect(panel, color=(0.05, 0.58, 0.60), fill=(0.94, 0.985, 0.985), width=1.1, overlay=True)
    bar = fitz.Rect(panel.x0, panel.y0, panel.x1, panel.y0 + H * 0.056)
    page.draw_rect(bar, color=(0.05, 0.58, 0.60), fill=(0.05, 0.58, 0.60), overlay=True)
    page.insert_text((bar.x0 + 12, bar.y0 + bar.height * 0.70), "교수 설명 · 개념 해설 · 심화 연결",
                     fontname="KRB", fontfile=bold, fontsize=12.0, color=(1, 1, 1), overlay=True)

    inner = fitz.Rect(panel.x0 + 14, bar.y1 + 10, panel.x1 - 14, panel.y1 - 12)
    h1 = inner.height * 0.54
    h2 = inner.height * 0.20
    r1 = fitz.Rect(inner.x0, inner.y0, inner.x1, inner.y0 + h1)
    r2 = fitz.Rect(inner.x0, r1.y1 + 3, inner.x1, r1.y1 + 3 + h2)
    r3 = fitz.Rect(inner.x0, r2.y1 + 3, inner.x1, inner.y1)
    heads = [
        ("교수 설명 전체 요약", time_label, (0.02, 0.30, 0.55)),
        ("쉽게 이해하기", "", (0.02, 0.55, 0.55)),
        ("관련·심화·연구 연결", "", (0.43, 0.24, 0.62)),
    ]
    bodies = [
        speech or "이 구간은 화면 전환 중심이므로 강의자료와 시각 흐름을 근거로 해설한다.",
        sec.get("easy") or sec.get("slide") or "슬라이드의 제어변수, 관측량, 경계조건을 먼저 구분한다.",
        " ".join(x for x in [sec.get("deep"), sec.get("research")] if x) or "관련 물리과정과 적용조건을 독립 실험으로 교차검증한다.",
    ]
    for rect, (head, label, col), body in zip([r1, r2, r3], heads, bodies):
        y = rect.y0
        page.insert_text((rect.x0, y + 10), head, fontname="KRB", fontfile=bold, fontsize=9.6, color=col, overlay=True)
        if label:
            fit_text(page, fitz.Rect(rect.x0 + rect.width * 0.52, y + 1, rect.x1, y + 15), label,
                     "KR", reg, 6.5, 6.0, (0.35, 0.42, 0.48), 1.0, fitz.TEXT_ALIGN_RIGHT)
        page.draw_line((rect.x0, y + 15), (rect.x1, y + 15), color=(0.70, 0.80, 0.84), width=0.5, overlay=True)
        bodyrect = fitz.Rect(rect.x0, y + 20, rect.x1, rect.y1 - 3)
        fit_text(page, bodyrect, body, "KR", reg, 8.0 if rect == r1 else 7.7, 6.2, (0.06, 0.15, 0.24), 1.28)

    page.draw_rect(bottom, color=(0.04, 0.25, 0.48), fill=(0.91, 0.95, 0.98), width=1.0, overlay=True)
    tag = fitz.Rect(bottom.x0, bottom.y0, bottom.x0 + W * 0.13, bottom.y1)
    page.draw_rect(tag, color=(0.04, 0.25, 0.48), fill=(0.04, 0.25, 0.48), overlay=True)
    fit_text(page, fitz.Rect(tag.x0 + 6, tag.y0 + 4, tag.x1 - 6, tag.y1 - 4), "핵심 정리\n및 요약",
             "KRB", bold, 8.4, 7.0, (1, 1, 1), 1.15)
    fit_text(page, fitz.Rect(tag.x1 + 10, bottom.y0 + 6, bottom.x1 - 10, bottom.y1 - 6), summary,
             "KRB", bold, 8.0, 6.4, (0.03, 0.17, 0.32), 1.22)


def add_text_appendix(doc: fitz.Document, title: str, lines: list[str], reg: str, bold: str,
                      toc: list[list[Any]], level: int = 1) -> None:
    if not lines:
        return
    W, H = 1024, 576
    idx = 0
    first = True
    while idx < len(lines):
        p = doc.new_page(width=W, height=H)
        if first:
            toc.append([level, title, p.number + 1])
            first = False
        p.draw_rect(fitz.Rect(0, 0, 10, H), fill=(0.04, 0.58, 0.60), color=None)
        p.insert_text((32, 42), title, fontname="KRB", fontfile=bold, fontsize=22, color=(0.04, 0.22, 0.42))
        p.draw_line((32, 58), (990, 58), color=(0.05, 0.58, 0.60), width=1.2)
        for col in [fitz.Rect(32, 76, 500, 542), fitz.Rect(524, 76, 992, 542)]:
            chunk: list[str] = []
            while idx < len(lines):
                test = "\n".join(chunk + [lines[idx]])
                if len(test) > 4300 and chunk:
                    break
                chunk.append(lines[idx])
                idx += 1
            fit_text(p, col, "\n".join(chunk), "KR", reg, 7.5, 6.2, (0.05, 0.12, 0.20), 1.22)
            if idx >= len(lines):
                break
        fit_text(p, fitz.Rect(900, 552, 990, 572), str(p.number + 1), "KR", reg, 7, 6.5,
                 (0.35, 0.42, 0.48), 1.0, fitz.TEXT_ALIGN_RIGHT)


def validate_render(doc: fitz.Document) -> dict[str, Any]:
    blank: list[int] = []
    for i, p in enumerate(doc):
        pix = p.get_pixmap(matrix=fitz.Matrix(0.25, 0.25), colorspace=fitz.csGRAY, alpha=False)
        data = bytes(pix.samples)
        if not data or (max(data) - min(data) < 3 and len(p.get_text().strip()) < 20):
            blank.append(i + 1)
    return {"blank_pages": blank}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    work = ensure_dir(out.parent / "work")
    transcript_dir = ensure_dir(out.parent / "transcripts")
    base = work / "base.pdf"
    download(cfg["base_pdf_url"], base)

    transcripts: dict[str, list[dict[str, Any]]] = {}
    for key, spec in cfg["videos"].items():
        transcripts[key] = get_transcript(key, spec, work, transcript_dir, cfg.get("whisper_model", "medium"))

    doc = fitz.open(base)
    reg, bold = font_paths()
    mappings: list[dict[str, Any]] = []
    source_count = 0
    mapped_segments: dict[str, set[int]] = {k: set() for k in transcripts}

    for page in list(doc):
        text = page.get_text("text")
        ident = identify_page(text)
        if not ident:
            continue
        kind, number = ident
        source_count += 1
        sections = existing_sections(text)
        groups: list[tuple[str, float, float, list[dict[str, Any]]]] = []
        if kind == "electro":
            key = "electro_260907" if number <= 34 else "video_project"
            interval = extract_interval(text)
            if interval:
                a, b = interval
                groups.append((key, a, b, transcripts[key]))
                for j, s in enumerate(transcripts[key]):
                    if s["end"] > a and s["start"] < b:
                        mapped_segments[key].add(j)
        else:
            for key, mapping in [("pemfc_260914", PEMFC_260914), ("pemfc_260916", PEMFC_260916)]:
                if number in mapping:
                    a, b = mapping[number]
                    groups.append((key, a, b, transcripts[key]))
                    for j, s in enumerate(transcripts[key]):
                        if s["end"] > a and s["start"] < b:
                            mapped_segments[key].add(j)

        speech, time_label, char_count = combine_speech(groups)
        if not speech:
            speech = sections.get("slide") or sections.get("easy") or "강의자료의 핵심 구조와 시각적 강조를 기준으로 해설한다."
            time_label = "강의자료·시각 정합"
        speech = dedup_sentences(speech)
        summary = make_summary(sections.get("core", ""), speech, sections.get("easy", ""), sections.get("deep", ""))
        draw_panel(page, speech, time_label, sections, summary, reg, bold)
        mappings.append({"pdf_page": page.number + 1, "kind": kind, "slide_page": number,
                         "time_ranges": time_label, "speech_chars": char_count})

    if source_count != 115:
        raise RuntimeError(f"source page count mismatch: {source_count}/115")

    toc = doc.get_toc(simple=True)
    toc.append([1, "부록 - 전체 교정 전사와 정합 감사", doc.page_count + 1])
    for key, spec in cfg["videos"].items():
        lines: list[str] = []
        for i, s in enumerate(transcripts[key]):
            mark = "" if i in mapped_segments[key] else " [슬라이드 전환/도입·종결 구간]"
            lines.append(f"[{sec_to_stamp(s['start'])}-{sec_to_stamp(s['end'])}]{mark} {s['text']}")
        add_text_appendix(doc, f"전체 교정 전사 - {spec['filename']}", lines, reg, bold, toc, 2)
    map_lines = [f"PDF p.{m['pdf_page']:03d} | {m['kind']} p.{m['slide_page']:02d} | {m['time_ranges']} | speech {m['speech_chars']} chars" for m in mappings]
    add_text_appendix(doc, "슬라이드-음성 정합표", map_lines, reg, bold, toc, 2)
    doc.set_toc(toc)

    tmp = out.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=4, deflate=True, clean=True)
    doc.close()
    os.replace(tmp, out)

    check = fitz.open(out)
    render = validate_render(check)
    all_text = "\n".join(p.get_text("text") for p in check)
    bad = {x: all_text.count(x) for x in ["를 설명한다.를 설명한다.", "의 인과관계를 앞뒤 페이지와 연결한다.", "�", "尀", "[["]}
    if render["blank_pages"]:
        raise RuntimeError(f"blank pages: {render['blank_pages']}")
    if any(bad.values()):
        raise RuntimeError(f"bad strings remain: {bad}")

    qa: dict[str, Any] = {
        "source_pages_identified": source_count,
        "source_pages_required": 115,
        "final_pages": check.page_count,
        "file_size_bytes": out.stat().st_size,
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "mapped_pages": len(mappings),
        "bad_strings": bad,
        **render,
        "transcripts": {},
    }
    for key, spec in cfg["videos"].items():
        segs = transcripts[key]
        qa["transcripts"][key] = {
            "filename": spec["filename"],
            "duration_seconds": spec["duration"],
            "segments": len(segs),
            "coverage_ratio": round(transcript_coverage(segs, spec["duration"]), 4),
            "mapped_segments": len(mapped_segments[key]),
            "mapped_ratio": round(len(mapped_segments[key]) / max(1, len(segs)), 4),
        }
    check.close()
    (out.parent / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    with (out.parent / "mapping.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["pdf_page", "kind", "slide_page", "time_ranges", "speech_chars"])
        writer.writeheader()
        writer.writerows(mappings)
    log(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
