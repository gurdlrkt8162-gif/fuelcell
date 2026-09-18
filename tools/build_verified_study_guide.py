from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Iterable

import fitz  # PyMuPDF
import requests

BASE_PDF_URL = "https://sdmntprcentralus.oaiusercontent.com/files/00000000-ae70-81f5-8850-309601e4c5c1/raw?se=2026-09-18T07%3A12%3A49Z&sp=r&sv=2026-02-06&sr=b&scid=7f191ab8-1dbc-53cf-8875-c7324c2dd559&skoid=9063adf3-a524-4acf-b70a-8731b33f2f50&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2026-09-18T00%3A47%3A29Z&ske=2026-09-19T00%3A47%3A29Z&sks=b&skv=2026-02-06&sig=GrFPLHKXTtrvfijndjn5aoSFfr04gDG/PHW87EFCdr4%3D"
OUT_DIR = Path("dist")
BASE_PATH = OUT_DIR / "base.pdf"
FINAL_PATH = OUT_DIR / "hydrogen_energy_complete_guide_verified.pdf"
QA_PATH = OUT_DIR / "qa_report.json"

NAVY = (0.035, 0.145, 0.329)
TEAL = (0.020, 0.569, 0.588)
PALE_BLUE = (0.969, 0.980, 1.000)
PALE_MINT = (0.929, 0.988, 0.969)
TEXT = (0.059, 0.149, 0.271)
MUTED = (0.258, 0.341, 0.431)
WHITE = (1, 1, 1)
ORANGE = (0.92, 0.45, 0.12)

FONT_REG_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
]
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
]


def first_existing(paths: Iterable[str]) -> str:
    for path in paths:
        if Path(path).exists():
            return path
    raise FileNotFoundError(f"No font found from: {list(paths)}")


FONT_REG = first_existing(FONT_REG_CANDIDATES)
FONT_BOLD = first_existing(FONT_BOLD_CANDIDATES)


def download_base() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(BASE_PDF_URL, timeout=120)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Downloaded base is not a PDF")
    BASE_PATH.write_bytes(response.content)


def register_fonts(page: fitz.Page) -> None:
    page.insert_font(fontname="NBG", fontfile=FONT_REG)
    page.insert_font(fontname="NBG-B", fontfile=FONT_BOLD)


def textbox(page: fitz.Page, rect: fitz.Rect, text: str, *, size: float = 9.0,
            color=TEXT, bold: bool = False, align=0, lineheight: float = 1.30) -> float:
    font = "NBG-B" if bold else "NBG"
    current = size
    while current >= 5.8:
        result = page.insert_textbox(
            rect, text, fontname=font, fontsize=current, color=color,
            align=align, lineheight=lineheight, overlay=True,
        )
        if result >= -0.1:
            return current
        current -= 0.25
    raise RuntimeError(f"Text overflow in {rect}: {text[:80]}")


def heading(page: fitz.Page, number: str, title: str, subtitle: str) -> None:
    page.draw_rect(fitz.Rect(36, 24, 83, 62), color=TEAL, fill=TEAL, width=0.7)
    textbox(page, fitz.Rect(36, 34, 83, 58), number, size=14, color=WHITE, bold=True, align=1)
    textbox(page, fitz.Rect(99, 25, 685, 58), title, size=20, color=NAVY, bold=True)
    textbox(page, fitz.Rect(36, 67, 690, 87), subtitle, size=8.6, color=MUTED)
    page.draw_line(fitz.Point(36, 91), fitz.Point(684, 91), color=TEAL, width=1.0)


def card(page: fitz.Page, rect: fitz.Rect, title: str, body: str,
         *, fill=PALE_BLUE, accent=NAVY, body_size=8.5) -> None:
    page.draw_rect(rect, color=accent, fill=fill, width=0.8)
    page.draw_rect(fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + 28), color=accent, fill=accent, width=0.8)
    textbox(page, fitz.Rect(rect.x0 + 12, rect.y0 + 7, rect.x1 - 12, rect.y0 + 25), title,
            size=10.5, color=WHITE, bold=True)
    textbox(page, fitz.Rect(rect.x0 + 13, rect.y0 + 37, rect.x1 - 13, rect.y1 - 12), body,
            size=body_size, color=TEXT, lineheight=1.34)


def keybar(page: fitz.Page, text: str) -> None:
    page.draw_rect(fitz.Rect(36, 354, 684, 389), color=NAVY, fill=(0.91, 0.95, 0.99), width=0.8)
    page.draw_rect(fitz.Rect(36, 354, 126, 389), color=NAVY, fill=NAVY, width=0.8)
    textbox(page, fitz.Rect(42, 365, 120, 385), "핵심 정리", size=9.2, color=WHITE, bold=True, align=1)
    textbox(page, fitz.Rect(139, 360, 674, 385), text, size=8.2, color=NAVY, bold=True, lineheight=1.22)


def replace_evidence_card(doc: fitz.Document, page_number: int, text: str) -> None:
    page = doc[page_number - 1]
    register_fonts(page)
    rect = fitz.Rect(25, 245, 336, 348)
    page.draw_rect(rect, color=NAVY, fill=PALE_BLUE, width=0.8, overlay=True)
    page.draw_rect(fitz.Rect(25, 245, 336, 270), color=NAVY, fill=NAVY, width=0.8, overlay=True)
    textbox(page, fitz.Rect(39, 251, 322, 267), "교수 설명 정합 요약 · 전사/화면 근거",
            size=9.5, color=WHITE, bold=True)
    textbox(page, fitz.Rect(39, 278, 322, 340), text, size=7.4, color=TEXT, lineheight=1.28)


def add_audit_page(doc: fitz.Document, number: str, title: str, subtitle: str,
                   left_title: str, left_body: str, right_title: str, right_body: str,
                   key: str) -> None:
    page = doc.new_page(width=720, height=405)
    register_fonts(page)
    page.draw_rect(page.rect, fill=WHITE, color=WHITE)
    heading(page, number, title, subtitle)
    card(page, fitz.Rect(36, 108, 350, 337), left_title, left_body, fill=PALE_BLUE, accent=NAVY, body_size=8.25)
    card(page, fitz.Rect(370, 108, 684, 337), right_title, right_body, fill=PALE_MINT, accent=TEAL, body_size=8.25)
    keybar(page, key)


def add_table_page(doc: fitz.Document, number: str, title: str, subtitle: str,
                   columns: list[tuple[str, float]], rows: list[list[str]], key: str,
                   font_size: float = 7.2) -> None:
    page = doc.new_page(width=720, height=405)
    register_fonts(page)
    page.draw_rect(page.rect, fill=WHITE, color=WHITE)
    heading(page, number, title, subtitle)
    x0, y0, width = 36.0, 107.0, 648.0
    header_h, row_h = 25.0, min(18.5, 218.0 / max(1, len(rows)))
    x = x0
    for label, frac in columns:
        w = width * frac
        page.draw_rect(fitz.Rect(x, y0, x + w, y0 + header_h), color=NAVY, fill=NAVY, width=0.7)
        textbox(page, fitz.Rect(x + 5, y0 + 6, x + w - 5, y0 + header_h - 3), label,
                size=8.0, color=WHITE, bold=True, align=1)
        x += w
    y = y0 + header_h
    for r, row in enumerate(rows):
        fill = (0.97, 0.985, 1.0) if r % 2 == 0 else WHITE
        x = x0
        for (label, frac), value in zip(columns, row):
            w = width * frac
            page.draw_rect(fitz.Rect(x, y, x + w, y + row_h), color=(0.62, 0.72, 0.81), fill=fill, width=0.45)
            textbox(page, fitz.Rect(x + 4, y + 3, x + w - 4, y + row_h - 2), value,
                    size=font_size, color=TEXT, lineheight=1.13)
            x += w
        y += row_h
    keybar(page, key)


def build() -> dict:
    download_base()
    doc = fitz.open(BASE_PATH)
    if len(doc) != 117:
        raise RuntimeError(f"Unexpected base page count: {len(doc)}")

    replace_evidence_card(doc, 3,
        "직접 확인된 전사 [00:00–00:59] : 조교는 강의가 전기화학 분석의 필요성과 기본개념, 선형주사전위법(LSV)을 먼저 다룬다고 설명한다. 자료에는 EIS도 포함되지만 이 영상은 LSV까지 진행하며, 식을 전부 암기하기보다 분석 목적과 물리량의 의미를 이해하라고 안내한다. 이후 페이지별 축어전문은 미노출이므로 화면 순서와 85쪽 자료를 기준으로 정합했다.")
    replace_evidence_card(doc, 37,
        "직접 확인된 전사 [02:50–02:53] : 손현택 조교는 이전 수업에 이어 이번 강의에서 전기화학 임피던스 분광법(EIS)을 다룬다고 명시한다. 이후 페이지별 축어전문은 미노출이므로 p.35–85의 화면 순서와 강의자료를 기준으로 입력파형→복소 임피던스→Nyquist/Bode→ECM→유효성→피팅→DRT→응용의 흐름을 정합했다.")
    replace_evidence_card(doc, 88,
        "직접 확인된 전사 [00:00–01:01] : 조교는 전기화학 분석 다음 단계로 PEMFC의 작동원리, membrane·catalyst·GDL·bipolar plate의 역할, 실제 조립과 test station을 세 부분으로 설명한다고 안내한다. PEMFC는 양성자를 전달하는 고분자막을 사용하는 연료전지라고 소개한다. 이후 전문은 미노출이므로 화면과 30쪽 강의자료로 정합했다.")
    replace_evidence_card(doc, 103,
        "직접 확인된 전사 [01:15–01:59] : 조교는 GDL을 단순 가스 전달층이 아니라 반응물 수송, 전자·열전도, 물관리의 다기능 층으로 설명한다. Channel의 H₂와 공기를 촉매층에 고르게 분배하고 전자와 열을 외부로 전달한다고 설명한다. ASR의 ‘전자 및 10 전도’는 화면과 강의자료를 근거로 ‘전자 및 열전도’로 교정했다.")

    add_audit_page(doc, "A1", "음성 전사 완전성과 페이지 정합의 실제 범위",
        "4개 영상 모두 completed이지만 무료 계정에서는 전체 전문이 아닌 일부 transcript preview만 노출된다.",
        "직접 확인된 사실",
        "• 260907 기초 전기화학: 38:35, ko-KR, 00:00–00:59 미리보기\n"
        "• Video Project: 55:46, ko-KR, 02:50–02:53 미리보기\n"
        "• 260914 PEMFC: 18:04, ko-KR, 00:00–01:01 미리보기\n"
        "• 260916 PEMFC: 15:46, ko-KR, 01:15–01:59 미리보기\n\n"
        "네 파일의 처리 완료 상태와 강의 길이는 확인했지만 전체 SRT/VTT 또는 전체 문장 transcript는 현재 연결에 제공되지 않았다.",
        "페이지별 설명을 만드는 원칙",
        "1. 강의자료가 직접 제시하는 식·그림·용어를 정본으로 삼는다.\n"
        "2. 전사 미리보기에서 직접 확인한 발언에는 시간범위를 붙인다.\n"
        "3. 미노출 구간은 화면의 슬라이드 순서와 앞뒤 논리로 의미 보존형 요약을 작성한다.\n"
        "4. 표준이론·연구동향은 강의자의 발언으로 쓰지 않는다.\n"
        "5. 슬라이드 하나와 원인 하나를 일대일로 자동 귀속하지 않는다.",
        "‘전사 처리 완료’와 ‘전체 전문 확보’는 다르다. 이 판본은 확인된 발언과 화면 정합을 엄격히 구분한다.")

    add_audit_page(doc, "A2", "AccurateScribe 전문용어 교정과 직접 발언 요약",
        "자동자막은 강의자료의 표기·화학식·화면 문맥으로 교정하되, 발언에 없던 내용을 추가하지 않는다.",
        "전사 미리보기에서 직접 확인한 강의 흐름",
        "260907 : 전기화학 분석의 필요성→기본개념→LSV를 먼저 다루고 EIS는 후속 강의로 연결. 식 암기보다 의미 이해를 강조.\n\n"
        "Video Project : 이전 수업에 이어 EIS를 본격적으로 다룬다는 도입.\n\n"
        "260914 : PEMFC 작동원리→membrane/catalyst/GDL/bipolar plate→조립/test station의 3부 구조.\n\n"
        "260916 : GDL의 반응물 수송, 전자·열전도, 물관리 기능을 설명.",
        "정상화한 대표 ASR 오류",
        "linnial sweet boltarmatry → Linear Sweep Voltammetry\n"
        "전기화학 인피던스 분권법 → 전기화학 임피던스 분광법\n"
        "PAMFC / PFC → PEMFC\n"
        "Mambrane → membrane\nCatalist → catalyst\n"
        "Gasdiffersion Layer → gas diffusion layer\n"
        "Bipularprate → bipolar plate\n"
        "전자 및 10 전도 → 전자 및 열전도\n\n"
        "수식과 화학기호는 음성 추정이 아니라 공식 강의자료를 정본으로 사용했다.",
        "전문용어 교정은 발음을 매끄럽게 만드는 작업이 아니라, 슬라이드·수식·앞뒤 문맥으로 의미를 복원하는 검증 절차다.")

    electro_rows = [
        ["p.1–2", "강의 제목·목차", "260907 화면순서", "도입 전사 직접확인"],
        ["p.3–20", "전기화학 개요·제어방식·CI", "260907 화면순서+자료", "축어전문 미노출"],
        ["p.21–34", "LSV·scan rate·가역성·응용", "260907 화면순서+자료", "축어전문 미노출"],
        ["p.35–41", "EIS 입력·복소수·Nyquist/Bode", "Video Project 화면순서", "EIS 도입 직접확인"],
        ["p.42–58", "R/C/CPE/Warburg·ECM", "Video Project 화면순서+자료", "축어전문 미노출"],
        ["p.59–77", "유효성·회로선택·피팅", "Video Project 화면순서+자료", "축어전문 미노출"],
        ["p.78–85", "DRT·PEMFC/SOFC 응용", "Video Project 화면순서+자료", "축어전문 미노출"],
    ]
    add_table_page(doc, "A3", "전기화학 강의자료 85쪽과 두 영상의 정합 지도",
        "260907은 개요·LSV, Video Project는 EIS·ECM·DRT를 담당한다. 시간은 직접 전사와 시각 정합을 구분한다.",
        [("자료 범위", .13), ("핵심 주제", .37), ("정합 근거", .28), ("음성 상태", .22)],
        electro_rows,
        "전기화학 85쪽의 순서와 두 영상의 역할은 일치한다. 다만 전체 문장별 발언은 미노출이므로 의미 보존형 해설로 한정한다.", 7.6)

    pemfc_rows1 = [
        ["1", "00:00–00:47", "강의 목표·범위"], ["2", "00:47–02:08", "기본 반응·전하 이동"],
        ["3", "02:08–03:38", "연료전지 종류"], ["4", "03:38–04:37", "Nafion 구조"],
        ["5", "04:37–05:48", "층상 구조"], ["6", "05:48–06:39", "막의 역할"],
        ["7", "06:39–07:28", "이온클러스터"], ["8", "07:28–08:36", "vehicle·Grotthuss"],
        ["9", "08:36–09:38", "수화율·전도도"], ["10", "09:38–11:09", "전기삼투·역확산"],
        ["11", "11:09–11:47", "수분분포·면적저항"], ["12", "11:47–12:37", "촉매층"],
        ["13", "12:37–13:27", "촉매 조건"], ["14", "13:27–14:57", "Sabatier·ORR"],
        ["15", "14:57–17:08", "Pt 합금·지지체"], ["16–17", "17:08–17:12", "GDL 역할·미세구조"],
    ]
    add_table_page(doc, "A4", "260914 PEMFC 영상–강의자료 정합 1/2",
        "화면 전환을 기준으로 한 시각 정합 시간이며, 정확한 문장 타임코드와는 구분한다.",
        [("자료 p.", .13), ("화면 구간", .27), ("주제", .60)], pemfc_rows1,
        "p.1–17은 영상 화면과 강의자료가 순서대로 대응한다. 음성 직접인용은 00:00–01:01 미리보기 범위에 한정한다.", 7.0)

    pemfc_rows2 = [
        ["18–21", "260914 미표시", "GDL/MPL·분리판·유로", "강의자료+260916 보강"],
        ["22", "17:12–17:14", "엔드플레이트", "260914 화면"],
        ["23", "17:14–17:24", "부품 확인", "260914 화면"],
        ["24", "17:24–17:28", "첫 분리판", "260914 화면"],
        ["25", "17:28–17:32", "가스켓", "260914 화면"],
        ["26", "17:32–17:38", "MEA 적층", "260914 화면"],
        ["27", "17:38–17:47", "반복 적층", "260914 화면"],
        ["28", "17:47–17:56", "최종 압축", "260914 화면"],
        ["29–30", "17:56–18:04", "Test station", "260914 화면"],
        ["16 이후", "01:15 이후", "GDL·부품·실습 후속", "260916 preview+화면"],
    ]
    add_table_page(doc, "A5", "PEMFC 영상–강의자료 정합 2/2",
        "260914가 건너뛴 p.18–21은 260916 후속 강의와 강의자료를 결합하되, 미노출 음성을 만들지 않는다.",
        [("자료 p.", .13), ("화면 구간", .22), ("주제", .36), ("근거", .29)], pemfc_rows2,
        "260914와 260916은 상호보완적이다. 정확한 발언이 노출되지 않은 p.18–30은 화면·자료·확인된 GDL 설명으로 범위를 제한한다.", 7.2)

    add_audit_page(doc, "A6", "정합성·학습자 친화성·과학정확성 QA",
        "원 슬라이드의 주장, 교수 발언, 외부 보강을 구분하고 수식·단위·적용조건을 독립적으로 확인했다.",
        "정량 검사",
        "• 원 강의자료: 전기화학 85/85, PEMFC 30/30\n"
        "• AccurateScribe completed: 4/4 영상\n"
        "• 영상 총길이: 2:08:13\n"
        "• 직접 노출된 전사 구간: 4개 미리보기\n"
        "• 최종 PDF: 원본 117쪽 + 감사 부록 6쪽\n"
        "• 모든 페이지 크기: 720×405 pt\n"
        "• 빈 페이지·깨진 문자·제어문자 검사 실시\n"
        "• 핵심 페이지 4곳의 전사 정합 설명을 직접 교체",
        "엄격한 해석 원칙",
        "• LSV의 onset·peak를 고유상수로 단정하지 않는다.\n"
        "• EIS의 좋은 fit을 유일한 물리모델로 간주하지 않는다.\n"
        "• DRT peak 개수를 물리과정 개수와 자동 동일시하지 않는다.\n"
        "• 막 수화와 cathode flooding을 같은 ‘물 문제’로 합치지 않는다.\n"
        "• GDL·MPL·유로·압축·test station을 경계조건과 수송망으로 연결한다.\n"
        "• 실험실 결과를 stack/system/mission으로 확대할 때 별도 검증을 요구한다.",
        "이 PDF는 페이지별 학습서로 배포할 수 있지만, AccurateScribe 전체 export 없이 ‘모든 발언의 완전 축어복원본’이라고 부를 수는 없다.")

    doc.set_metadata({
        "title": "수소에너지 실험 완전학습서 — 페이지별 정합 엄격검증판",
        "author": "OpenAI",
        "subject": "전기화학 분석, LSV, EIS/ECM/DRT, PEMFC 원리·부품·조립·시험·진단",
        "keywords": "electrochemistry, PEMFC, LSV, EIS, DRT, lecture alignment, verified study guide",
    })
    toc = [[1, "학습서 본문", 1], [1, "음성·영상 정합 감사", 118]]
    doc.set_toc(toc)
    doc.save(FINAL_PATH, garbage=4, deflate=True, clean=True)
    doc.close()

    check = fitz.open(FINAL_PATH)
    expected_pages = 123
    if len(check) != expected_pages:
        raise RuntimeError(f"Unexpected final page count: {len(check)}")
    sizes = {(round(p.rect.width, 2), round(p.rect.height, 2)) for p in check}
    if sizes != {(720.0, 405.0)}:
        raise RuntimeError(f"Inconsistent page sizes: {sizes}")
    all_text = "\n".join(p.get_text("text") for p in check)
    broken_counts = {s: all_text.count(s) for s in ["�", "尀", "[[", "\x00"]}
    if any(broken_counts.values()):
        raise RuntimeError(f"Broken text detected: {broken_counts}")
    blank_pages = []
    rendered = []
    for idx in [0, 1, 2, 36, 87, 102, 117, 118, 119, 120, 121, 122]:
        page = check[idx]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), colorspace=fitz.csGRAY, alpha=False)
        samples = pix.samples
        nonwhite = sum(1 for b in samples if b < 248) / max(1, len(samples))
        rendered.append({"page": idx + 1, "nonwhite_ratio": round(nonwhite, 5)})
        if nonwhite < 0.006:
            blank_pages.append(idx + 1)
    check.close()
    if blank_pages:
        raise RuntimeError(f"Possible blank pages: {blank_pages}")
    digest = hashlib.sha256(FINAL_PATH.read_bytes()).hexdigest()
    qa = {
        "file": FINAL_PATH.name,
        "bytes": FINAL_PATH.stat().st_size,
        "sha256": digest,
        "pages": expected_pages,
        "page_size_pt": [720, 405],
        "source_slides": {"electrochemistry": 85, "pemfc": 30},
        "accuratescribe_completed_videos": 4,
        "total_video_duration_seconds": 7692.56,
        "direct_transcript_preview_ranges": 4,
        "replaced_evidence_cards": [3, 37, 88, 103],
        "appendix_pages": 6,
        "broken_text_counts": broken_counts,
        "representative_render_checks": rendered,
        "blank_pages": blank_pages,
        "release_scope": "source-faithful integrated study guide; not a full verbatim transcript",
    }
    QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))
    return qa


if __name__ == "__main__":
    build()
