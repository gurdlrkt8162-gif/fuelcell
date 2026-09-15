from __future__ import annotations

import json
from pathlib import Path
import fitz
from PIL import Image, ImageChops


def crop_white(img: Image.Image, pad: int = 12) -> Image.Image:
    rgb = img.convert('RGB')
    bg = Image.new('RGB', rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg).convert('L')
    # Ignore very light antialiasing and page shadow.
    mask = diff.point(lambda p: 255 if p > 14 else 0)
    bbox = mask.getbbox()
    if not bbox:
        return rgb
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(rgb.width, x1 + pad)
    y1 = min(rgb.height, y1 + pad)
    cropped = rgb.crop((x0, y0, x1, y1))
    # Do not overcrop source slides: retain at least 86% of each dimension.
    if cropped.width < rgb.width * 0.86 or cropped.height < rgb.height * 0.86:
        return rgb
    return cropped


def render(pdf_path: Path, out_dir: Path, prefix: str) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    manifest: list[dict] = []
    matrix = fitz.Matrix(2.15, 2.15)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csRGB)
        raw = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        raw = crop_white(raw)
        # Scale to a stable maximum width while preserving detail.
        max_w = 1800
        if raw.width > max_w:
            h = round(raw.height * max_w / raw.width)
            raw = raw.resize((max_w, h), Image.Resampling.LANCZOS)
        name = f'{prefix}{i+1:03d}.jpg'
        path = out_dir / name
        raw.save(path, 'JPEG', quality=88, optimize=True, progressive=True)
        text = page.get_text('text').replace('\x00', '').strip()
        manifest.append({
            'page': i + 1,
            'file': str(path).replace('\\', '/'),
            'width': raw.width,
            'height': raw.height,
            'text': text[:3500],
        })
    return manifest


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / '_source'
    out = root / 'study_guide_assets'
    electro = render(source / 'electrochemistry.pdf', out / 'electro', 'e')
    pemfc = render(source / 'pemfc.pdf', out / 'pemfc', 'p')
    (out / 'manifest.json').write_text(
        json.dumps({'electro': electro, 'pemfc': pemfc}, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'rendered electro={len(electro)} pemfc={len(pemfc)}')


if __name__ == '__main__':
    main()
