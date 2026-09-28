from __future__ import annotations
import runpy
from pathlib import Path

source_path = Path(__file__).with_name('build_hydrogen_complete_final.py')
patched_path = Path(__file__).with_name('_build_hydrogen_complete_final_fixed.py')
s = source_path.read_text(encoding='utf-8')

# Make HTML font resolution portable: use the font directory as a PyMuPDF archive
# and relative font filenames in @font-face.
s = s.replace(
    "CSS='''",
    "ARCHIVE=fitz.Archive(str(Path(FONT).parent))\nCSS='''",
    1,
)
s = s.replace(
    ".replace('NANUM_REG',Path(FONT).as_uri()).replace('NANUM_BOLD',Path(FONT_B).as_uri())",
    ".replace('NANUM_REG',Path(FONT).name).replace('NANUM_BOLD',Path(FONT_B).name)",
)

# All HTML layout calls must receive the archive so the embedded Korean fonts resolve.
s = s.replace(
    "css=CSS,scale_low=0.72,overlay=True)",
    "css=CSS,archive=ARCHIVE,scale_low=0.72,overlay=True)",
)
s = s.replace(
    "css=CSS,scale_low=0.76,overlay=True)",
    "css=CSS,archive=ARCHIVE,scale_low=0.76,overlay=True)",
)
s = s.replace(
    "css=CSS,scale_low=.8)",
    "css=CSS,archive=ARCHIVE,scale_low=.8)",
)

# Direct text insertion is used only for concise labels / QA rows. Use MuPDF's
# built-in Korean CJK font, avoiding malformed embedded font descriptors.
s = s.replace("page.insert_font(fontname='nanum',fontfile=FONT);page.insert_font(fontname='nanumb',fontfile=FONT_B)\n", "")
s = s.replace("p=doc.new_page(width=1024,height=576);p.insert_font(fontname='nanum',fontfile=FONT);p.insert_font(fontname='nanumb',fontfile=FONT_B)", "p=doc.new_page(width=1024,height=576)")
s = s.replace("fontname='nanumb'", "fontname='korea'")
s = s.replace("fontname='nanum'", "fontname='korea'")

# Guard that every expected patch was applied before executing a costly build.
checks = {
    'archive_created': 'ARCHIVE=fitz.Archive' in s,
    'relative_font_urls': "Path(FONT).name" in s,
    'panel_archive': 'archive=ARCHIVE,scale_low=0.72' in s,
    'summary_archive': 'archive=ARCHIVE,scale_low=0.76' in s,
    'qa_archive': 'archive=ARCHIVE,scale_low=.8' in s,
    'no_direct_nanum': "fontname='nanum'" not in s and "fontname='nanumb'" not in s,
}
failed = [k for k,v in checks.items() if not v]
if failed:
    raise RuntimeError(f'Patch contract failed: {failed}')

patched_path.write_text(s, encoding='utf-8')
runpy.run_path(str(patched_path), run_name='__main__')
