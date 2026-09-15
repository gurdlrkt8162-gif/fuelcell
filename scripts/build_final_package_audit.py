#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path

CHUNK = 16 * 1024 * 1024
MAX_PACKAGE_BYTES = 5_250_000_000
REQUIRED_MARKERS = {
    "PEMFC FC01": ["01_PEMFC", "FC01"],
    "PEMFC FC02": ["01_PEMFC", "FC02"],
    "PEMFC FC17": ["01_PEMFC", "FC17"],
    "PEMFC FC06 purge": ["01_PEMFC", "FC06"],
    "Battery NASA": ["02_BATTERY", "BAT01"],
    "Battery CALCE LFP": ["02_BATTERY", "BAT03"],
    "Mission CMU UAV": ["03_MISSION", "MIS01"],
    "Mission USV": ["03_MISSION", "MIS04"],
    "BoP MetroPT": ["04_BOP", "BOP01"],
    "Supercapacitor": ["05_SUPERCAP", "SC01"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def classify(path: Path) -> tuple[str, str]:
    with path.open("rb") as f:
        head = f.read(512)
    low = head.lower().lstrip()
    if low.startswith(b"<!doctype html") or low.startswith(b"<html") or b"<html" in low[:200]:
        if path.suffix.lower() not in {".html", ".htm"}:
            raise RuntimeError(f"HTML response disguised as data: {path}")
        return "html", head[:32].hex()
    if head.startswith(b"PK\x03\x04") or head.startswith(b"PK\x05\x06") or head.startswith(b"PK\x07\x08"):
        return "zip", head[:32].hex()
    if head.startswith(b"MATLAB") or head.startswith(b"\x89HDF"):
        return "mat", head[:32].hex()
    if head.startswith(b"%PDF"):
        return "pdf", head[:32].hex()
    if path.suffix.lower() in {".csv", ".tsv", ".txt", ".names", ".md", ".json", ".jsonld", ".yml", ".yaml"}:
        return "text", head[:32].hex()
    return "binary", head[:32].hex()


def zip_integrity(path: Path) -> tuple[str, int, str]:
    if not zipfile.is_zipfile(path):
        return "not_zip", 0, ""
    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            return ("pass" if bad is None else "fail", len(zf.infolist()), bad or "")
    except Exception as exc:
        return "error", 0, repr(exc)


def marker_found(paths: list[str], parts: list[str]) -> bool:
    parts_low = [p.lower() for p in parts]
    for path in paths:
        low = path.lower()
        if all(part in low for part in parts_low):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    audit = root / "99_AUDIT"
    audit.mkdir(parents=True, exist_ok=True)

    candidates = sorted(
        p for p in root.rglob("*")
        if p.is_file() and audit not in p.parents and not p.name.endswith(".part")
    )
    part_files = sorted(p for p in root.rglob("*.part") if p.is_file())
    if part_files:
        raise RuntimeError(f"Incomplete .part files remain: {[str(p) for p in part_files[:10]]}")
    if not candidates:
        raise RuntimeError("Package has no data files")

    rel_paths = [p.relative_to(root).as_posix() for p in candidates]
    missing = [name for name, parts in REQUIRED_MARKERS.items() if not marker_found(rel_paths, parts)]
    if missing:
        raise RuntimeError(f"Required datasets missing: {missing}")

    rows: list[dict] = []
    zip_rows: list[dict] = []
    by_sha: dict[str, list[str]] = defaultdict(list)
    errors: list[dict] = []
    total = 0
    started = time.time()

    for index, path in enumerate(candidates, 1):
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total += size
        try:
            kind, magic = classify(path)
            digest = sha256_file(path)
            by_sha[digest].append(rel)
            zip_status, zip_entries, zip_bad = zip_integrity(path) if kind == "zip" or path.suffix.lower() == ".zip" else ("not_zip", 0, "")
            if zip_status in {"fail", "error"}:
                raise RuntimeError(f"ZIP integrity {zip_status}; bad={zip_bad}")
            row = {
                "path": rel,
                "size_bytes": size,
                "sha256": digest,
                "kind": kind,
                "extension": path.suffix.lower(),
                "magic_hex": magic,
                "zip_status": zip_status,
                "zip_entries": zip_entries,
            }
            rows.append(row)
            if zip_status != "not_zip":
                zip_rows.append({"path": rel, "size_bytes": size, "status": zip_status, "entries": zip_entries, "bad_entry": zip_bad})
            print(f"[{index}/{len(candidates)}] verified {rel} ({size} bytes)", flush=True)
        except Exception as exc:
            errors.append({"path": rel, "size_bytes": size, "error": repr(exc)})
            print(f"ERROR {rel}: {exc}", file=sys.stderr, flush=True)

    duplicates = {sha: paths for sha, paths in by_sha.items() if len(paths) > 1}
    if errors:
        (audit / "AUDIT_ERRORS.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError(f"Strict audit failed for {len(errors)} files")

    with (audit / "FINAL_FILE_MANIFEST.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    (audit / "FINAL_FILE_MANIFEST.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with (audit / "SHA256SUMS.txt").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(f"{row['sha256']}  {row['path']}\n")
    with (audit / "ZIP_INTEGRITY.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields = ["path", "size_bytes", "status", "entries", "bad_entry"]
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(zip_rows)
    (audit / "DUPLICATE_SHA256.json").write_text(json.dumps(duplicates, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "root": str(root),
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data_file_count": len(rows),
        "zip_file_count": len(zip_rows),
        "total_data_bytes_before_artifact_packaging": total,
        "total_data_GB_decimal": round(total / 1e9, 6),
        "duplicate_sha256_groups": len(duplicates),
        "strict_errors": 0,
        "required_markers": REQUIRED_MARKERS,
        "elapsed_seconds": round(time.time() - started, 3),
        "artifact_size_guard_bytes": MAX_PACKAGE_BYTES,
    }
    (audit / "PACKAGE_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    if total > MAX_PACKAGE_BYTES:
        raise RuntimeError(f"Package content {total} bytes exceeds single-artifact guard {MAX_PACKAGE_BYTES}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
