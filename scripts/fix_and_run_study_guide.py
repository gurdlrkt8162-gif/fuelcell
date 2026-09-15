from __future__ import annotations

import re
import fitz
from PIL import Image

import build_study_guide_pages as b


def extract_page(pdf: fitz.Document, idx: int):
    page = pdf[idx]
    # Preserve paragraph/line boundaries for title and bullet extraction.
    text = page.get_text('text').replace('\x00', '').replace('\u200b', '').strip()
    pix = page.get_pixmap(matrix=fitz.Matrix(1.85, 1.85), alpha=False, colorspace=fitz.csRGB)
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    return text, img


def wrap_px(draw, text: str, font, max_w: int) -> list[str]:
    # Normalize unsafe typography without collapsing intentional newlines.
    raw = (text or '').replace('\x00', ' ').replace('\u200b', '')
    raw = raw.replace('–', '-').replace('—', '-').replace('‒', '-')
    raw = raw.replace('“', '"').replace('”', '"').replace('’', "'")
    out: list[str] = []
    for raw_para in raw.splitlines():
        para = re.sub(r'[ \t\r\f\v]+', ' ', raw_para).strip()
        if not para:
            out.append('')
            continue
        # Korean text may not have reliable word boundaries; retain words when
        # possible, then fall back to character-level splitting for long tokens.
        tokens = para.split(' ')
        expanded: list[str] = []
        for token in tokens:
            if draw.textbbox((0, 0), token, font=font)[2] <= max_w:
                expanded.append(token)
            else:
                expanded.extend(list(token))
        line = ''
        for token in expanded:
            joiner = '' if len(token) == 1 and (not line or len(line[-1:]) == 1) else ' '
            candidate = token if not line else line + joiner + token
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_w:
                line = candidate
            else:
                if line:
                    out.append(line)
                line = token
        if line:
            out.append(line)
    return out


b.extract_page = extract_page
b.wrap_px = wrap_px
b.main()
