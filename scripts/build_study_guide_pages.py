from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path
from typing import Iterable

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1600, 900
NAVY = '#10346B'
NAVY2 = '#082B60'
TEAL = '#139AA0'
TEAL_DARK = '#087D83'
LIGHT_BLUE = '#EAF4FC'
LIGHT_TEAL = '#E8F8F7'
PALE = '#F7FAFD'
TEXT = '#172A45'
MUTED = '#50657E'
BORDER = '#3C76A8'
ORANGE = '#E78A27'
WHITE = '#FFFFFF'

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / '_source'
OUT = ROOT / 'study_guide_final_pages'
ASSET = ROOT / 'study_guide_assets'


def font_path(bold: bool = False) -> str:
    candidates = [
        '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf' if bold else '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf' if bold else '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if bold else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    raise FileNotFoundError('Korean font not found')


FONT = font_path(False)
FONT_B = font_path(True)

def F(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def clean(s: str) -> str:
    s = s.replace('\x00', ' ').replace('\u200b', '')
    s = s.replace('–', '-').replace('—', '-').replace('‒', '-')
    s = s.replace('“', '"').replace('”', '"').replace('’', "'")
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def wrap_px(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    text = clean(text)
    if not text:
        return []
    out: list[str] = []
    for para in text.split('\n'):
        para = para.strip()
        if not para:
            out.append('')
            continue
        words = list(para) if ' ' not in para else para.split(' ')
        line = ''
        for token in words:
            candidate = token if not line else (line + ('' if ' ' not in para else ' ') + token)
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_w:
                line = candidate
            else:
                if line:
                    out.append(line)
                line = token
        if line:
            out.append(line)
    return out


def fit_text(draw, text: str, box, start=20, min_size=13, bold=False, leading=1.34):
    x, y, w, h = box
    for size in range(start, min_size - 1, -1):
        font = F(size, bold)
        lines = wrap_px(draw, text, font, w)
        step = int(size * leading)
        if len(lines) * step <= h:
            return font, lines, step
    font = F(min_size, bold)
    lines = wrap_px(draw, text, font, w)
    return font, lines[: max(1, h // int(min_size * leading))], int(min_size * leading)


def draw_text(draw, text: str, box, start=20, min_size=13, color=TEXT, bold=False, leading=1.34):
    x, y, w, h = box
    font, lines, step = fit_text(draw, text, box, start, min_size, bold, leading)
    yy = y
    for line in lines:
        draw.text((x, yy), line, font=font, fill=color)
        yy += step
    return yy


def rounded(draw, box, fill, outline=BORDER, radius=14, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fit_image(img: Image.Image, box, bg=WHITE) -> Image.Image:
    x, y, w, h = box
    canvas = Image.new('RGB', (w, h), bg)
    im = img.convert('RGB')
    ratio = min(w / im.width, h / im.height)
    nw, nh = max(1, round(im.width * ratio)), max(1, round(im.height * ratio))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(im, ((w - nw) // 2, (h - nh) // 2))
    return canvas


def extract_page(pdf: fitz.Document, idx: int):
    page = pdf[idx]
    text = clean(page.get_text('text'))
    pix = page.get_pixmap(matrix=fitz.Matrix(1.85, 1.85), alpha=False, colorspace=fitz.csRGB)
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    return text, img

GENERIC_HEADERS = {
    '기초 전기화학 분석', '전기화학 분석의 기초', '전기화학분석법: 선형주사전위법 (LSV)',
    '전기화학분석법: 전기화학임피던스분광법 (EIS)', '양성자교환막 연료전지 (PEMFC)',
    '수소에너지 실험', 'PEMFC 이론 및 실험 실습 기초'
}


def title_from_text(text: str, page_num: int, kind: str) -> str:
    raw = [clean(x) for x in text.splitlines() if clean(x)]
    candidates = []
    for line in raw:
        if line in GENERIC_HEADERS or line == str(page_num):
            continue
        if len(line) < 3 or line.startswith('•'):
            continue
        if re.fullmatch(r'\d+', line):
            continue
        candidates.append(line)
    if candidates:
        t = candidates[0]
        if len(t) > 52:
            t = t[:49] + '...'
        return t
    return f'{kind} 강의자료 p.{page_num}'


def source_bullets(text: str, max_items=5) -> list[str]:
    lines = [clean(x) for x in text.splitlines() if clean(x)]
    out: list[str] = []
    for line in lines:
        if line in GENERIC_HEADERS or re.fullmatch(r'\d+', line):
            continue
        line = re.sub(r'^[•·\-]+\s*', '', line)
        if len(line) < 8:
            continue
        if line not in out:
            out.append(line)
        if len(out) >= max_items:
            break
    return out


TOPICS = {
'overview': {
'easy':'전기화학 분석은 전압과 전류를 단순히 읽는 작업이 아니라, 계면 반응·이온 이동·물질전달이 만드는 신호를 역으로 해석하는 과정이다. 먼저 무엇을 제어했고 무엇을 측정했는지 구분하면 서로 다른 기법도 한 체계로 연결된다.',
'related':'핵심 축은 평형전위, 전하전달 속도, 오믹 손실, 물질전달, 시간응답이다. 같은 곡선 변화도 온도·농도·표면상태·장비대역폭에서 올 수 있으므로 메타데이터를 함께 기록해야 한다.',
'advanced':'연구에서는 단일 곡선보다 perturbation 실험과 교차진단을 설계한다. 최근에는 physics-informed 모델, Bayesian 추정, 자동화된 실험계획을 결합해 매개변수 불확도까지 보고하는 방향이 강화되고 있다.',
'key':'전기화학 데이터는 입력-전달-계면-관측-추정의 순서로 읽는다.'},
'fuelcell_analysis': {
'easy':'연료전지 시험은 셀 자체만 보는 것이 아니라 가스·가습·압력·온도·부하를 동시에 제어하는 시스템 실험이다. 분극곡선은 전체 손실을, current interrupt는 빠른 오믹 성분을, EIS는 시간상수별 반응을 분리해 보여준다.',
'related':'성능·설계·내구 평가는 서로 연결된다. 막 저항, 촉매 반응, 기체확산, 접촉저항과 물관리는 분극곡선과 임피던스 모두에 영향을 준다. 운전점이 달라지면 같은 셀도 다른 제한 메커니즘을 보일 수 있다.',
'advanced':'최신 연구는 operando 진단과 디지털 트윈을 결합해 상태를 실시간 추정하고, 그 결과를 열·공기·수소·부하 제어의 제약으로 전달한다. 측정 위치와 gross/net power 경계를 명확히 해야 시스템 해석이 닫힌다.',
'key':'연료전지 분석은 셀 신호와 시험설비 경계조건을 함께 해석해야 한다.'},
'in_situ': {
'easy':'In situ는 작동 중 전체 시스템의 실제 손실을 보며, ex situ는 분리한 소재의 구조·조성·고유특성을 정밀하게 본다. 둘은 경쟁 방법이 아니라 원인 규명을 위한 상보적 단계다.',
'related':'In situ에서 관찰한 성능 저하를 ex situ의 현미경·분광·표면분석으로 확인하면 상관관계가 인과관계에 가까워진다. 반대로 ex situ 변화가 실제 운전 중 손실로 이어지는지도 다시 in situ에서 검증해야 한다.',
'advanced':'최근에는 operando X-ray, neutron imaging, Raman/IR, spatially resolved current mapping을 사용해 물·열·반응 분포를 동시에 관찰한다. 다만 측정창과 센서 자체가 유동·열장을 교란할 수 있어 기준 실험이 필요하다.',
'key':'In situ와 ex situ를 왕복해야 시스템 손실과 소재 변화가 연결된다.'},
'redox': {
'easy':'산화는 화학종이 전자를 전극으로 내놓는 과정이고, 환원은 전극의 전자를 화학종이 받는 과정이다. 외부회로의 전자 이동과 전해질의 이온 이동이 계면 반응에서 만나야 전류가 지속된다.',
'related':'전극반응은 전자전달만이 아니라 반응물의 접근, 흡착, 결합 절단·형성, 생성물 이탈을 포함한다. 가장 느린 단계와 표면 피복률이 전체 속도를 결정할 수 있다.',
'advanced':'다단계 반응은 하나의 전자수나 Tafel slope로 고유하게 식별되지 않는다. 동위원소, 회전전극, 생성물 분석, 전위계단과 EIS를 함께 사용해 가능한 기작을 단계적으로 배제한다.',
'key':'전극반응은 전자전달과 이온·물질 이동이 결합된 계면 과정이다.'},
'control_modes': {
'easy':'Potentiostatic은 전위를 고정하고 전류 응답을 읽으며, galvanostatic은 전류를 고정하고 전압 응답을 읽는다. 정상상태에서는 같은 운전점으로 수렴할 수 있지만 과도상태에서는 제어변수가 달라 응답경로도 달라진다.',
'related':'정상상태 분극곡선은 충분한 안정화 시간과 동일한 가스·온도·습도 조건이 필요하다. current interrupt는 전류를 급변시켜 빠른 전압강하와 느린 회복을 시간축으로 분리한다.',
'advanced':'제어기 대역폭, current range 전환, 필터와 sampling rate가 과도응답을 왜곡할 수 있다. 실제 연구에서는 command와 measured waveform, settling criterion, hysteresis를 함께 보존한다.',
'key':'제어한 변수와 응답변수를 분리해야 정상상태와 동특성을 정확히 비교할 수 있다.'},
'instruments': {
'easy':'Potentiostat/galvanostat의 성능은 단순 최대 전압·전류가 아니라 입력 임피던스, 전류분해능, 대역폭, compliance, 접지와 케이블에 의해 결정된다. 실험 신호가 장비의 정확도 영역 안에 있는지 먼저 확인해야 한다.',
'related':'EIS에서는 주파수별 accuracy contour, stray capacitance, cable inductance가 중요하고, 빠른 CV·CA에서는 rise time과 sampling이 중요하다. 고전류 연료전지는 booster와 전자부하 경계도 검토한다.',
'advanced':'장비 사양은 조건부다. 셀 임피던스와 케이블 조합에 따라 안정영역이 달라지므로 dummy cell과 표준 RC 회로로 사전 검증하고, raw range·overload flag를 데이터와 함께 저장한다.',
'key':'장비 사양표가 아니라 실제 셀-케이블-주파수 조합의 정확도와 안정성을 검증한다.'},
'method_map': {
'easy':'정상상태 i-V는 전체 성능을, CV/LSV는 전위에 따른 반응을, current interrupt는 빠른 전압성분을, EIS는 주파수별 시간상수를 본다. 질문이 다르므로 그래프 모양만 직접 비교하면 안 된다.',
'related':'시간불변·시간가변이라는 분류는 입력이 아니라 시스템 상태가 측정 동안 유지되는지까지 포함한다. 느린 EIS 저주파 측정 중 drift가 생기면 선형 주파수응답이라는 전제가 깨진다.',
'advanced':'최신 진단은 여러 기법을 동일 운전점에서 결합하고, 각 특징의 timestamp·freshness·uncertainty를 상태추정기에 전달한다. 특징값 자체보다 측정조건과 유효성 플래그가 중요하다.',
'key':'기법은 그래프가 아니라 제어입력, 시간척도, 추정하려는 물리량으로 선택한다.'},
'lsv_intro': {
'easy':'LSV는 작업전극 전위를 일정 속도로 한 방향으로 바꾸면서 전류를 측정한다. 전위가 반응의 구동력을 바꾸고, 전류는 전자전달·표면상태·물질공급의 결합 결과로 나타난다.',
'related':'3전극계에서는 WE-RE 전위를 제어하고 WE-CE 사이 전류를 흘린다. 기준전극은 전류를 거의 운반하지 않아야 하며, 지지전해질과 iR 보정이 실제 계면전위를 결정한다.',
'advanced':'LSV의 scan rate는 실험 시간척도다. 반응·확산·흡착·피막 시간과 비교해 가역성 및 peak 위치가 달라진다. scan-rate series와 blank, 반복주사를 함께 설계해야 한다.',
'key':'LSV 전류는 전위만의 함수가 아니라 scan rate와 수송·표면 이력의 함수다.'},
'nonfaradaic': {
'easy':'반응이 시작되기 전에도 이중층 충전, 전극·전해질 background, 케이블과 잡음 때문에 전류가 완전히 0일 필요는 없다. 이 구간은 반응전류를 빼기 위한 baseline을 정하는 데 중요하다.',
'related':'이중층 전류는 이상적으로 C_dl·dE/dt에 비례한다. 따라서 scan rate가 커지면 비패러데이 background도 커지고, 표면거칠기와 흡착에 따라 단순 평탄선이 아닐 수 있다.',
'advanced':'촉매 ECSA 추정에서는 특정 전위창의 흡착/탈착 또는 double-layer capacitance를 사용하지만, 면적 환산계수와 baseline 선택이 결과를 좌우한다. 동일 protocol과 불확도 보고가 필요하다.',
'key':'초기 전류를 0으로 가정하지 말고 background와 계면충전을 먼저 정량화한다.'},
'onset': {
'easy':'Onset potential은 전류가 배경에서 유의하게 벗어나기 시작한 지점이다. 하지만 threshold, tangent, 정규화 방식에 따라 값이 달라지므로 열역학적 고유상수처럼 취급하면 안 된다.',
'related':'onset은 촉매속도뿐 아니라 loading, 면적정규화, scan rate, iR, mass transfer, noise floor에 영향을 받는다. 서로 다른 연구를 비교할 때 동일 정의가 필수다.',
'advanced':'정량 비교에는 고정 전류밀도 전위, kinetic current, Tafel region, mass activity 같은 추가 지표를 함께 사용한다. 자동 onset 검출은 threshold sensitivity를 보고해야 한다.',
'key':'Onset은 정의된 분석지표이며, 정의와 보정조건을 함께 제시해야 비교 가능하다.'},
'peak': {
'easy':'Peak current는 전위가 커지며 반응이 빨라지는 효과와, 표면 근처 반응물이 고갈되는 효과가 교차할 때 나타난다. 전극 형상과 실험 시간척도에 따라 peak 대신 plateau가 나타날 수도 있다.',
'related':'가역 평면확산계에서 peak current는 농도·면적·전자수·확산계수와 scan rate의 제곱근에 연결된다. peak potential과 peak separation은 전하전달 속도와 iR에도 민감하다.',
'advanced':'흡착, 핵생성, 피막, coupled chemistry가 있으면 peak 높이와 위치가 단순 Randles-Sevcik에서 벗어난다. scan-rate scaling과 생성물·표면분석으로 기작을 구분한다.',
'key':'Peak는 반응속도와 확산 고갈의 경쟁 결과이며 모든 LSV의 필수 특징은 아니다.'},
'diffusion': {
'easy':'Peak 이후 전류가 줄어드는 가장 흔한 이유는 전극 표면의 반응물이 소모되어 공급이 따라오지 못하기 때문이다. 그러나 표면피막, 흡착, 후속반응도 비슷한 감소를 만들 수 있다.',
'related':'평면 전극의 비정상 확산층은 대략 sqrt(Dt)로 성장한다. RDE처럼 대류로 경계층을 고정하면 peak 대신 정상상태 plateau에 가까워진다.',
'advanced':'전류 감소 원인을 판별하려면 농도, scan rate, 회전속도, 전극크기와 반복주사를 바꾼다. 서로 다른 perturbation에 같은 확산계수가 재현될 때 모델 신뢰도가 높아진다.',
'key':'전류 감소를 확산 하나로 단정하지 말고 시간·유동·표면 perturbation으로 분리한다.'},
'scan_rate': {
'easy':'Scan rate를 높이면 같은 전위범위를 더 짧게 통과하므로 확산층이 얇고 농도구배가 커져 전류가 증가한다. 동시에 장비·iR·계면용량 영향도 커진다.',
'related':'가역 평면확산에서는 i_p가 sqrt(v)에 비례하지만, 직선성이 곧 가역성을 증명하지는 않는다. 비가역계도 특정 조건에서 유사한 scaling을 보일 수 있다.',
'advanced':'log(i_p)-log(v) 기울기, peak shift, 정방향/역방향, 농도·온도 의존성을 함께 분석한다. adsorption-controlled 과정은 이상적으로 i_p가 v에 더 가깝게 비례한다.',
'key':'Scan rate는 반응과 수송을 구분하는 시간축이며 전류 크기만 비교하면 부족하다.'},
'randles': {
'easy':'Randles-Sevcik 식은 가역 전자전달과 평면 반무한확산 조건에서 peak current를 n, A, D, C, scan rate와 연결한다. 계수는 단위계와 온도에 따라 달라진다.',
'related':'식에 넣는 면적은 기하학적 면적인지 ECSA인지 구분하고, 농도 단위와 scan rate 단위를 맞춰야 한다. R이 초기에 없고 용액이 정지해 있다는 가정도 확인한다.',
'advanced':'D와 n을 동시에 미지수로 두면 식 하나로 고유하게 분리되지 않는다. 독립 D 측정, 농도 series, RRDE 또는 생성물 분석으로 정보량을 보완한다.',
'key':'Randles-Sevcik은 단위와 가정이 맞을 때만 peak current를 물성으로 바꾸는 식이다.'},
'nernst': {
'easy':'Nernst 식은 산화형과 환원형의 활동도 비가 평형전위를 어떻게 바꾸는지 설명한다. 실제 peak potential은 평형전위에 kinetics, diffusion, iR가 더해진 결과다.',
'related':'표준전위 E0는 활동도 기반이고, 형식전위 E0-prime은 특정 전해질·pH·착물조건의 효과를 포함한다. 농도형 식을 다른 매질로 그대로 옮기면 안 된다.',
'advanced':'준가역·비가역계에서는 peak가 scan rate에 따라 이동한다. Nicholson/Laviron 계열 해석은 모델과 보정, 충분한 scan-rate 범위를 요구한다.',
'key':'평형전위, 형식전위, peak potential을 구분해야 열역학과 속도론이 섞이지 않는다.'},
'irreversible': {
'easy':'비가역 또는 준가역 반응에서는 전극이 주사되는 시간 안에 표면 조성이 평형을 따라가지 못해 peak가 이동하고 대칭성이 깨진다.',
'related':'관측 peak shift에는 표준속도상수, transfer coefficient, iR, 후속반응과 표면변화가 함께 들어간다. 단일 식의 회귀값을 고유한 기작상수로 해석하기 전에 residual을 본다.',
'advanced':'온도·scan rate·농도 series를 동시에 맞추는 global fitting과 Bayesian posterior를 사용하면 매개변수 상관성을 확인할 수 있다. 독립 실험으로 속도상수를 교차검증한다.',
'key':'비가역 peak 이동은 속도론 정보이지만 iR와 coupled chemistry를 분리해야 한다.'},
'fuelcell_polarization': {
'easy':'연료전지 분극곡선은 단일 전극 LSV peak가 아니라 셀 전류밀도에 따른 전체 전압손실을 보여준다. 저전류 활성화, 중전류 오믹, 고전류 물질전달 손실이 중첩된다.',
'related':'전력밀도는 P=V·j이며 최대전력점이 항상 최고효율점이나 최고내구점은 아니다. 가스, RH, 압력, 온도와 안정화 기준을 함께 보고해야 한다.',
'advanced':'최근 시스템 연구는 분극곡선, HFR, EIS/DRT, 셀전압 분포를 함께 사용해 안전운전영역을 구축한다. 이를 health-aware EMS의 출력·ramp·습도 제약으로 연결한다.',
'key':'분극곡선은 전체 셀 손실의 지도이며 운전조건과 안정화 기준이 데이터의 일부다.'},
'bioelectrochem': {
'easy':'바이오전극의 큰 전류는 생물학적 촉매가 전자전달을 촉진한다는 단서지만, 특정 생성물이 만들어졌다는 직접 증거는 아니다.',
'related':'메탄 생성 주장은 가스 조성, 탄소수지, coulombic/Faradaic efficiency, abiotic control을 필요로 한다. H2-mediated 경로와 direct electron transfer도 구분한다.',
'advanced':'미생물전기화학은 전극전위, biofilm mass transfer, mediator, microbial community가 결합된다. 전류와 생성물 수율을 함께 모델링해야 에너지·탄소 효율을 평가할 수 있다.',
'key':'전류증가는 반응 가능성의 증거이며 생성물과 경로는 별도 물질수지로 확인한다.'},
'eis_intro': {
'easy':'EIS는 작은 정현파 전압 또는 전류를 가하고 진폭비와 위상차를 주파수별로 측정한다. 각 주파수는 서로 다른 시간척도의 과정에 민감하다.',
'related':'복소 임피던스 Z=Z-prime+jZ-double-prime로 표현하며 Nyquist는 형상과 저항을, Bode는 주파수 위치와 위상을 읽기 쉽다. 두 선도는 같은 데이터를 다른 좌표로 본다.',
'advanced':'EIS 해석은 선형성, 정상성, 인과성, 유한성 전제가 필요하다. amplitude sweep, 반복측정, Kramers-Kronig consistency를 fitting 전에 확인한다.',
'key':'EIS는 주파수별 전달함수이며 데이터 유효성 검증이 등가회로 선택보다 먼저다.'},
'nyquist': {
'easy':'Nyquist plot은 x축에 Z-prime, y축에 보통 -Z-double-prime을 둔다. 고주파에서 시작해 저주파로 이동하며 절편·반원·꼬리의 순서로 읽는다.',
'related':'이상 Randles 회로에서 고주파 절편은 직렬저항, 반원 폭은 charge-transfer resistance, 저주파 꼬리는 확산과 연결된다. 실제 다공성 전극은 눌린 반원과 중첩을 보인다.',
'advanced':'반원 하나를 물리과정 하나로 자동 대응시키면 안 된다. ECM·DRT·운전조건 perturbation과 residual을 함께 사용해 assignment를 검증한다.',
'key':'Nyquist는 저항과 시간상수의 형상을 보여주지만 주파수 정보와 물리배정은 별도 확인한다.'},
'bode': {
'easy':'Bode plot은 주파수에 따른 |Z|와 phase를 직접 보여주므로 과정이 나타나는 주파수대와 시간상수를 찾기 쉽다.',
'related':'간단한 RC의 특성주파수는 f=1/(2πRC)이다. phase peak와 기울기 변화는 과정의 중심시간을 알려주지만 중첩·CPE·확산에서는 단순식이 달라진다.',
'advanced':'제어공학의 phase margin과 전기화학 Bode phase는 목적이 다르다. impedance 데이터만으로 폐루프 안정성을 직접 판정하지 않는다.',
'key':'Bode는 과정의 위치를 주파수축에서 읽고 Nyquist와 함께 해석한다.'},
'validity': {
'easy':'EIS는 측정 중 시스템이 거의 변하지 않고, 입력 크기에 비례해 응답하며, 미래 입력에 앞서 응답하지 않는다는 전제를 가진다.',
'related':'신호 진폭을 바꾸어 normalized impedance가 겹치는지, 순서를 바꿔 drift가 없는지, 동일 조건 반복이 재현되는지 확인한다.',
'advanced':'Kramers-Kronig 일관성은 데이터가 선형·인과적 LTI 계열과 양립하는지 보는 gate이지, 선택한 ECM이 물리적으로 유일하다는 인증이 아니다.',
'key':'EIS fitting 전에 선형성·정상성·인과성·재현성을 먼저 통과시킨다.'},
'ecm': {
'easy':'등가회로는 실제 전기화학 과정을 R, C, CPE, diffusion 요소로 근사해 측정 impedance를 설명하는 모델이다.',
'related':'R은 에너지 소산, C는 전하저장, R||C는 하나의 완화시간, Warburg는 확산응답을 나타낸다. 요소 연결은 전류·전압 경계와 물리적 직렬/병렬 관계를 반영해야 한다.',
'advanced':'요소를 추가하면 fit은 좋아지지만 식별성은 나빠질 수 있다. parameter correlation, confidence interval, residual structure와 독립 perturbation을 함께 본다.',
'key':'좋은 fit보다 최소한의 식별 가능한 회로와 물리적 검증이 중요하다.'},
'cpe': {
'easy':'CPE는 이상 커패시터에서 벗어난 분산된 계면응답을 Z=1/[Q(jω)^n]으로 표현한다. n=1이면 이상 C에 가까워진다.',
'related':'Q의 단위는 n에 따라 달라져 곧바로 capacitance가 아니다. 거칠기, 반응분포, 다공성, 시간상수 분산이 눌린 반원을 만들 수 있다.',
'advanced':'CPE를 물리과정 하나로 단정하지 말고 effective capacitance 변환식의 조건을 명시한다. geometry·온도·상태 perturbation에서 Q와 n의 일관성을 검증한다.',
'key':'CPE는 분산응답의 경험적 표현이며 Q를 그대로 capacitance로 부르면 안 된다.'},
'warburg': {
'easy':'Warburg impedance는 농도장이 주기적으로 확산할 때 생기는 주파수 의존 응답이다. 반무한확산에서는 Nyquist에서 약 45도 꼬리가 나타난다.',
'related':'실제 셀은 유한 두께·차단/투과 경계를 가지므로 저주파에서 수직 또는 수평에 가까운 유한길이 확산으로 바뀔 수 있다.',
'advanced':'기체용해, 막수송, 다공성 기공확산이 중첩되면 단일 Warburg 계수의 물리해석이 모호하다. 두께·유량·농도 perturbation으로 assignment를 구속한다.',
'key':'45도 선 하나만으로 확산 종류와 위치를 확정하지 않고 경계조건을 함께 모델링한다.'},
'measurement': {
'easy':'EIS 조건은 DC bias, 진폭, 주파수범위, points/decade, cycle 수, 안정화 기준으로 정의된다. 측정시간이 긴 저주파에서 drift가 가장 문제가 된다.',
'related':'기준전극 위치, 차폐, 접지, 케이블 길이, dummy cell, current range가 고주파 artifact를 좌우한다. 유도성 loop가 보이면 먼저 배선과 부하를 점검한다.',
'advanced':'자동 측정에서는 각 주파수의 coherence, residual, drift flag를 저장하고 유효하지 않은 point를 이유와 함께 제외한다. raw waveform 보존이 도움이 된다.',
'key':'EIS 품질은 회로 fitting보다 bias·진폭·주파수·배선·안정화 설계에서 결정된다.'},
'fitting': {
'easy':'Fitting은 회로 응답과 측정값의 차이를 최소화해 매개변수를 추정한다. 초기값, bounds와 weighting이 결과를 크게 바꿀 수 있다.',
'related':'실수·허수·modulus weighting은 서로 다른 영역을 강조한다. residual이 주파수에 따라 체계적으로 남으면 회로구조 또는 데이터 유효성이 부족한 것이다.',
'advanced':'여러 회로의 AIC/BIC, profile likelihood, bootstrap, Bayesian posterior를 비교해 식별성을 평가한다. 동일 데이터의 낮은 오차가 물리적 유일성을 뜻하지 않는다.',
'key':'매개변수 표만 보지 말고 residual, 상관성, 불확도와 대안모델을 함께 제시한다.'},
'drt': {
'easy':'DRT는 임피던스를 연속적인 완화시간 분포로 펼쳐 중첩된 과정을 시각화한다. 하지만 역문제가 ill-posed라 정칙화에 따라 peak가 생기거나 합쳐질 수 있다.',
'related':'주파수 범위 밖 과정은 안정적으로 복원되지 않으며 noise와 inductive/capacitive kernel 선택도 결과를 바꾼다. peak 면적·위치의 불확도를 같이 본다.',
'advanced':'2025 연구는 DRT의 사용자 선택 의존성과 모델가정을 다시 강조하고, Bayesian mixture와 frequency-band 기반 정칙화 선택으로 자동화·불확도 정량화를 시도한다.',
'key':'DRT peak는 물리과정의 후보이며 정칙화 민감도와 perturbation 검증 없이 확정하지 않는다.'},
'pemfc_eis': {
'easy':'PEMFC EIS에서는 고주파 저항이 막·접촉의 빠른 오믹 성분, 중주파가 전하전달, 저주파가 기체·물 수송에 민감한 경우가 많다.',
'related':'수소·산소 분압, RH, stoichiometry, pressure를 하나씩 바꾸면 각 arc/DRT peak의 반응을 통해 assignment를 검증할 수 있다.',
'advanced':'Dry-out과 flooding 모두 성능을 낮추지만 dry-out은 HFR 증가, flooding은 저주파 수송저항과 변동 증가가 두드러질 수 있다. 단일 주파수 지표는 셀·운전점별 보정이 필요하다.',
'key':'PEMFC EIS는 운전조건 perturbation과 HFR·분극곡선을 함께 써야 고장모드가 분리된다.'},
'sofc_eis': {
'easy':'SOFC EIS는 전극 반응, 가스전환·확산, 전해질·접촉 저항을 온도와 연료활용도에 따라 분리한다. 고온이라 반응시간과 열화기작이 PEMFC와 다르다.',
'related':'장기시험에서는 ohmic과 polarization resistance의 시간변화를 분리하고 셀별 분포를 본다. 연결재 부식과 접촉저항은 ohmic 증가로 나타날 수 있다.',
'advanced':'DRT와 온도·분압 perturbation을 결합하면 activation energy와 반응차수를 이용한 assignment가 가능하다. 장기 drift와 reference 상태 정의가 핵심이다.',
'key':'SOFC EIS는 온도·가스·연료활용도와 장기추세를 함께 해석한다.'},
'pemfc_reaction': {
'easy':'Anode에서 H2가 H+와 e-로 나뉘고, H+는 막을 통과하며 e-는 외부회로를 거쳐 일을 한다. Cathode에서 O2, H+, e-가 만나 물을 만든다.',
'related':'전체반응은 H2 + 1/2 O2 -> H2O이다. 1.23 V는 표준상태의 가역전압에 가까운 값이며 실제 전압은 활성화·오믹·수송 손실로 낮아진다.',
'advanced':'열역학 전압은 온도·분압·물 상태에 따라 Nernst 식으로 이동한다. 시스템 효율은 LHV/HHV 기준과 보조기기 소비를 구분해야 한다.',
'key':'PEMFC는 전자와 양성자의 경로를 분리해 화학에너지를 외부 전기일로 바꾼다.'},
'fuelcell_types': {
'easy':'연료전지는 전해질과 이동 이온에 따라 반응 위치, 재료, 온도와 연료허용도가 달라진다. PEMFC는 H+ 전도성 고분자막과 저온 운전이 특징이다.',
'related':'낮은 온도는 빠른 시동과 높은 출력밀도에 유리하지만 Pt 촉매, CO 오염, 막 수화·열관리가 중요해진다. 표의 효율은 운전점과 기준에 따라 달라진다.',
'advanced':'모빌리티 설계에서는 셀 효율뿐 아니라 compressor·humidifier·coolant pump의 net system efficiency, 동특성, 내구성과 수소저장을 함께 최적화한다.',
'key':'전해질과 전하운반체가 재료·온도·오염민감도와 시스템 구성을 결정한다.'},
'layer_stack': {
'easy':'PEMFC는 분리판-GDL-촉매층-막-촉매층-GDL-분리판이 겹친 다층 반응기다. 각 층은 전자, 양성자, 기체, 물과 열의 서로 다른 통로를 제공한다.',
'related':'성능은 층의 고유물성뿐 아니라 계면접촉, 압축, ionomer 분포, 기공 연결성과 젖음성에 좌우된다. MEA라는 용어의 포함범위도 문헌마다 선언이 필요하다.',
'advanced':'최근 연구는 촉매층의 nm-scale ionomer film부터 GDL·유로 mm-scale까지 연결하는 multiscale model과 operando imaging을 결합한다.',
'key':'층 이름보다 다섯 수송망과 계면의 연속성을 추적해야 PEMFC가 이해된다.'},
'membrane': {
'easy':'PFSA 막은 소수성 불소계 골격과 친수성 술폰산기를 함께 가져, 물이 찬 이온 domain에서 양성자가 이동한다.',
'related':'좋은 막은 낮은 protonic resistance, 낮은 gas/electron permeability, 기계·화학 내구성을 동시에 요구한다. 얇게 만들수록 저항은 줄지만 crossover와 pinhole 위험이 커질 수 있다.',
'advanced':'연구동향은 강화 초박막 PFSA, 저습용 hydrocarbon membrane, radical 안정화, 계면 ionomer 설계다. 막 성능은 EW, 두께, water uptake, swelling, conductivity와 crossover를 함께 보고한다.',
'key':'막은 양성자를 통과시키면서 전자와 반응가스를 차단해야 하는 선택적 수송막이다.'},
'proton_transport': {
'easy':'Vehicle은 H3O+ 같은 수화종이 이동하는 그림이고, Grotthuss는 수소결합망을 따라 proton defect가 hopping하는 그림이다. 실제 PFSA에서는 둘이 함께 기여한다.',
'related':'수화가 부족하면 이온 domain 연결성이 떨어지고, 온도를 올려도 탈수 때문에 전도도가 오히려 악화될 수 있다. 물 함량과 morphology가 핵심이다.',
'advanced':'전도도 모델은 막종류·EW·온도·water activity·이력에 의존한다. MD/mesoscale 연구는 나노채널 연결성과 국소 산성도, confined water 구조를 해석한다.',
'key':'양성자전도는 단일 메커니즘이 아니라 수화된 나노통로의 구조와 동역학의 결과다.'},
'hydration': {
'easy':'수화율 λ는 술폰산기 하나당 물분자 수를 뜻하며 막의 연결된 이온통로와 전도도를 압축해 나타낸다.',
'related':'inlet RH만으로 막 내부 λ가 결정되지 않는다. dew point, cell temperature, pressure, 생성수, electro-osmotic drag와 back diffusion이 함께 작용한다.',
'advanced':'최신 운전전략은 RH sensor 하나보다 HFR, 물수지 모델, outlet humidity와 압력강하를 융합해 막 수화 상태를 추정한다.',
'key':'λ는 막 내부 상태변수이며 가스 RH와 동일하지 않다.'},
'water_balance': {
'easy':'전류가 흐르면 양성자와 함께 물이 anode에서 cathode로 끌려가는 electro-osmotic drag가 생긴다. 농도구배는 반대 또는 같은 방향의 back diffusion을 만든다.',
'related':'총 water flux의 방향은 각 항의 부호와 λ(x) 기울기로 결정된다. 높은 전류에서 anode dry-out과 cathode flooding이 동시에 나타날 수 있다.',
'advanced':'water-balance map은 anode/cathode RH, stoichiometry, pressure, membrane thickness, temperature, current density를 축으로 구축한다. 상태추정·MPC의 핵심 제약이 된다.',
'key':'물관리는 drag·diffusion·생성·증발·배출의 동적 수지 문제다.'},
'membrane_asr': {
'easy':'막 내부 수분이 위치마다 다르면 전도도도 달라진다. 면적저항 ASR은 두께방향 1/σ를 적분한 값이므로 가장 건조한 구간이 큰 영향을 줄 수 있다.',
'related':'EIS high-frequency resistance에는 막뿐 아니라 접촉·전자저항과 장비 배선이 포함될 수 있다. 모델 ASR과 HFR을 비교할 때 경계를 맞춘다.',
'advanced':'분포형 막 모델은 λ(x)-σ(x)-ASR을 연결하고 neutron/X-ray water imaging, segmented cell, local temperature로 검증한다.',
'key':'평균 수화율보다 국소 건조구간이 막 저항과 내구성을 지배할 수 있다.'},
'catalyst': {
'easy':'촉매층은 Pt/C, ionomer와 pore가 얽힌 분포형 반응영역이다. 전자·양성자·기체가 동시에 도달하고 물이 빠져나가야 활성점이 실제 전류를 만든다.',
'related':'높은 intrinsic activity만으로 MEA 성능이 보장되지 않는다. ionomer film, oxygen resistance, Pt utilization, 탄소부식과 물포화가 함께 결정한다.',
'advanced':'2025-2026 저-PGM 연구는 ordered PtCo intermetallic, 보호 carbon shell, mesoporous support로 활성과 내구를 동시에 높이려 한다. MEA H2-air 내구검증이 중요하다.',
'key':'촉매층 성능은 촉매 입자보다 세 수송망과 반응영역의 연결성으로 결정된다.'},
'sabatier': {
'easy':'Sabatier 원리는 반응중간체가 너무 약하게도 너무 강하게도 결합하지 않을 때 촉매활성이 높다는 설명이다. volcano plot의 정상 부근이 균형점이다.',
'related':'ORR에서는 O, OH 등 중간체 결합에너지와 Pt 표면 전자구조가 중요하다. 합금·strain·ordering이 결합에너지를 조정한다.',
'advanced':'Volcano는 descriptor 기반 경향이며 실제 MEA의 ionomer·수송·내구를 포함하지 않는다. half-cell activity와 H2-air 성능·AST를 단계적으로 검증한다.',
'key':'최적 촉매는 중간체를 적당히 붙잡고 적당히 놓아주는 표면을 만든다.'},
'gdl': {
'easy':'GDL은 기체를 유로에서 촉매층으로 보내고 전자와 열을 전달하며 생성수를 제거한다. 높은 기공률과 전도도, 적절한 소수성, 기계적 지지가 동시에 필요하다.',
'related':'압축하면 접촉저항은 줄 수 있지만 기공이 닫혀 가스확산과 물배출이 나빠질 수 있다. rib/channel 아래의 비균일 압축이 local current와 flooding을 만든다.',
'advanced':'연구동향은 graded porosity/wettability, operando X-ray/neutron imaging, tomography 기반 수송모델이다. GDL 선택은 유로·압축·운전 RH와 함께 최적화한다.',
'key':'GDL은 기체·물·전자·열을 동시에 조절하는 다기능 다공성 부품이다.'},
'mpl': {
'easy':'MPL은 GDL과 촉매층 사이의 더 작은 기공층으로 접촉을 개선하고 물과 기체의 분포를 조절한다. PTFE와 carbon 구조가 capillary pressure를 바꾼다.',
'related':'MPL crack은 배수통로가 될 수도 있고 국소침수·접촉불균일을 만들 수도 있다. 두께·기공크기·소수성의 최적점이 있다.',
'advanced':'최근 연구는 pore-network와 직접수치해석을 operando saturation map과 연결해 liquid-water breakthrough와 oxygen resistance를 예측한다.',
'key':'MPL은 단순 전도층이 아니라 촉매층 계면의 물-기체 분배기다.'},
'bipolar': {
'easy':'분리판은 anode/cathode 가스를 분리하고 전자를 수집하며 셀을 지지하고 열과 물을 유로로 관리한다. 스택 질량·부피·압력강하에도 큰 영향을 준다.',
'related':'Graphite는 내식성과 전도성이 좋지만 두껍고 가공비가 크다. 금속판은 얇고 강하지만 부식·접촉저항 때문에 코팅과 표면처리가 필요하다.',
'advanced':'연구동향은 ultrathin stamped metal plate, 저비용 내식코팅, composite plate와 additive manufacturing이다. 접촉저항·부식전류·기밀·성형성을 함께 평가한다.',
'key':'분리판은 유로판이자 집전체·열경로·기계골격이며 시스템 power density를 좌우한다.'},
'flowfield': {
'easy':'Parallel은 압력강하가 작지만 분배불균일과 물정체에 민감하고, serpentine은 배수가 좋지만 blower/pump 부담이 크다. interdigitated는 GDL 관통대류를 강제한다.',
'related':'유로 선택은 평균 성능보다 channel/rib 아래 산소·수분·온도 분포와 압력손실의 균형문제다. purge와 manifold 설계도 스택 균일성에 중요하다.',
'advanced':'최신 연구는 topology optimization, CFD-porous coupling, digital twin을 이용해 유로·GDL·운전조건을 공동최적화한다.',
'key':'좋은 유로는 반응물 균일성·배수·압력강하·열관리를 동시에 균형화한다.'},
'endplate': {
'easy':'엔드플레이트와 체결부는 스택을 정렬하고 가스·전기 연결을 제공하며, gasket·MEA·분리판에 균일한 압력을 전달한다.',
'related':'압력이 부족하면 누설과 접촉저항이 커지고, 과도하면 GDL 기공붕괴·막손상·유로변형이 생긴다. torque가 곧 균일압력을 보장하지는 않는다.',
'advanced':'압축해석은 plate bending, bolt preload, gasket nonlinear stiffness와 thermal cycling을 포함한다. pressure-sensitive film과 contact resistance map으로 검증한다.',
'key':'스택 체결은 기밀·접촉·기공·내구를 동시에 정하는 구조설계 문제다.'},
'assembly': {
'easy':'조립은 분리판-가스켓-MEA-분리판을 방향과 유로에 맞춰 반복 적층하고, 정렬을 유지한 채 교차 순서로 단계적으로 체결한다.',
'related':'조립 전에는 gasket 손상, MEA 오염·주름, 유로 이물, 포트 정렬을 확인한다. 체결 후에는 불활성가스로 leak/crossover를 먼저 검사한다.',
'advanced':'연구·생산에서는 torque-angle, bolt elongation, compression map, 접촉저항과 leak rate를 lot별로 기록한다. 제조 variation이 셀전압 분산과 열화에 연결된다.',
'key':'조립 품질은 성능시험 전에 기밀·정렬·압축 균일성으로 검증한다.'},
'test_station': {
'easy':'테스트 스테이션은 regulator, MFC, humidifier, heater, BPR, load와 센서로 셀의 경계조건을 만든다. 측정장비가 아니라 실험조건 생성기다.',
'related':'가스유량은 stoichiometry, 가습은 dew point/RH, BPR은 절대압력·차압, load는 전류/전압 trajectory를 결정한다. 센서 위치와 line heat tracing도 기록한다.',
'advanced':'최신 station은 자동 interlock, recipe versioning, synchronized high-speed data, online EIS와 상태추정을 결합한다. 수소 purge·환기·LEL detector·fail-safe valve가 기본이다.',
'key':'테스트 스테이션의 제어오차와 안전로직까지 셀 데이터의 일부다.'},
}


def topic_for(kind: str, page: int, text: str) -> str:
    t = text.lower()
    if kind == 'pemfc':
        if page == 2: return 'pemfc_reaction'
        if page == 3: return 'fuelcell_types'
        if page == 5: return 'layer_stack'
        if page in (4,6,7): return 'membrane'
        if page == 8: return 'proton_transport'
        if page == 9: return 'hydration'
        if page == 10: return 'water_balance'
        if page == 11: return 'membrane_asr'
        if page in (12,13,15): return 'catalyst'
        if page == 14: return 'sabatier'
        if page in (16,17): return 'gdl'
        if page == 18: return 'mpl'
        if page in (19,20): return 'bipolar'
        if page == 21: return 'flowfield'
        if page == 22: return 'endplate'
        if 23 <= page <= 28: return 'assembly'
        if page in (29,30): return 'test_station'
        return 'overview'
    # electrochemistry
    if 4 <= page <= 7: return 'fuelcell_analysis'
    if page in (8,9): return 'in_situ'
    if page in (10,11): return 'redox'
    if 12 <= page <= 15: return 'control_modes'
    if page in (16,17): return 'instruments'
    if 18 <= page <= 20: return 'method_map'
    if page in (21,22): return 'lsv_intro'
    if page == 23: return 'nonfaradaic'
    if page == 24: return 'onset'
    if page == 25: return 'peak'
    if page == 26: return 'diffusion'
    if page in (27,28): return 'scan_rate'
    if page == 29: return 'randles'
    if page == 30: return 'nernst'
    if page in (31,32): return 'irreversible'
    if page == 33: return 'fuelcell_polarization'
    if page == 34: return 'bioelectrochem'
    if 'drt' in t: return 'drt'
    if 'pemfc' in t and ('eis' in t or 'impedance' in t): return 'pemfc_eis'
    if 'sofc' in t and ('eis' in t or 'impedance' in t): return 'sofc_eis'
    if 'nyquist' in t or '나이퀴스트' in t: return 'nyquist'
    if 'bode' in t or '보드' in t: return 'bode'
    if 'warburg' in t: return 'warburg'
    if 'cpe' in t or 'constant phase' in t: return 'cpe'
    if '피팅' in t or 'fitting' in t: return 'fitting'
    if '등가회로' in t or 'equivalent circuit' in t or 'ecm' in t: return 'ecm'
    if '측정 조건' in t or '파라데이 케이지' in t or '차폐' in t: return 'measurement'
    if '선형성' in t or '안정성' in t or '인과' in t or 'kramers' in t: return 'validity'
    if page >= 35: return 'eis_intro'
    return 'overview'


def visual_hint(topic: str) -> str:
    hints = {
        'overview':'제어량-측정량-추정량을 표와 화살표로 연결한다.',
        'fuelcell_analysis':'성능곡선·EIS·시험설비에서 공통 경계조건을 찾는다.',
        'in_situ':'전체 시스템 신호와 분리 시료 분석의 장단점을 대응한다.',
        'redox':'전자 화살표와 이온 경로, 산화·환원 위치를 함께 본다.',
        'control_modes':'무엇을 고정하고 무엇이 응답하는지 좌우 열을 비교한다.',
        'instruments':'정확도 contour와 주파수·전류 범위를 실제 실험조건에 대입한다.',
        'method_map':'각 그래프의 x축·y축·시간척도를 먼저 구분한다.',
        'lsv_intro':'전위 ramp와 voltammogram의 같은 시간위치를 대응한다.',
        'nonfaradaic':'반응 전 baseline과 이중층 전류가 완전한 0이 아님을 확인한다.',
        'onset':'onset을 정하는 기준선과 threshold가 어디인지 본다.',
        'peak':'상승하는 kinetics와 성장하는 고갈층이 교차하는 지점을 읽는다.',
        'diffusion':'peak 이후 농도고갈·피막·후속반응의 후보를 구분한다.',
        'scan_rate':'scan rate가 커질 때 peak 높이와 위치가 어떻게 변하는지 본다.',
        'randles':'식의 변수·단위와 i_p-sqrt(v) 직선성을 대응한다.',
        'nernst':'평형전위와 peak potential, 활동도와 농도 표현을 구분한다.',
        'irreversible':'scan rate 증가에 따른 peak 이동과 비대칭을 읽는다.',
        'fuelcell_polarization':'저·중·고 전류밀도의 지배손실과 power curve를 함께 본다.',
        'bioelectrochem':'전류곡선과 실제 생성물·가스분석 그래프를 분리해 읽는다.',
        'eis_intro':'입력과 출력 정현파의 진폭비·위상차를 Nyquist/Bode로 연결한다.',
        'nyquist':'고주파 시작점, 반원 폭, 저주파 꼬리와 주파수 방향을 확인한다.',
        'bode':'|Z|와 phase가 변하는 주파수대에서 시간상수를 찾는다.',
        'validity':'반복·진폭 변화·drift 검증 결과를 fitting 전에 확인한다.',
        'ecm':'회로 연결과 전기화학 경계의 직렬·병렬 관계를 대응한다.',
        'cpe':'눌린 반원과 n 값의 관계를 보되 Q를 곧바로 C로 읽지 않는다.',
        'warburg':'45도 꼬리와 유한길이 저주파 극한을 구분한다.',
        'measurement':'진폭·주파수·bias·배선·차폐 조건을 체크리스트로 읽는다.',
        'fitting':'측정점·모델선·residual을 함께 보고 체계적 편차를 찾는다.',
        'drt':'peak 위치·폭·정칙화 변화와 원래 EIS 재구성 오차를 함께 본다.',
        'pemfc_eis':'HFR·중주파 arc·저주파 transport와 RH/분압 변화를 대응한다.',
        'sofc_eis':'온도·연료활용도와 ohmic/polarization resistance 추세를 본다.',
        'pemfc_reaction':'전자·H+·O2·H2O의 경로와 반응식을 같은 방향으로 추적한다.',
        'fuelcell_types':'전해질·전하운반체·온도·촉매를 열별로 비교한다.',
        'layer_stack':'각 층이 운반하는 전자·양성자·기체·물·열을 색으로 연결한다.',
        'membrane':'소수성 backbone과 친수성 ion domain의 역할을 나눠 본다.',
        'proton_transport':'vehicle 이동과 proton hopping의 그림을 구분한다.',
        'hydration':'water activity-λ-전도도-온도 그래프의 입력·출력을 이어 본다.',
        'water_balance':'drag와 diffusion 화살표 방향, 식의 부호와 λ gradient를 본다.',
        'membrane_asr':'λ(x)-σ(x)-ASR의 순차 계산을 식과 분포그래프에서 찾는다.',
        'catalyst':'Pt/C-ionomer-pore의 세 연속망과 실제 반응영역을 본다.',
        'sabatier':'volcano 정상과 결합에너지 과약·과강 영역을 읽는다.',
        'gdl':'섬유 기공·압축·전자/열 경로와 물 배출을 함께 본다.',
        'mpl':'GDL과 촉매층 사이의 작은 기공·PTFE·crack 구조를 본다.',
        'bipolar':'가스분리·집전·지지·열·물관리 기능을 한 부품에서 찾는다.',
        'flowfield':'parallel·serpentine·interdigitated의 압력강하와 배수를 비교한다.',
        'endplate':'bolt preload가 gasket·GDL·plate에 어떻게 분배되는지 본다.',
        'assembly':'방향·정렬·가스켓·MEA·체결 순서를 체크리스트로 읽는다.',
        'test_station':'가스·가습·온도·압력·부하의 폐루프와 안전계통을 찾는다.',
    }
    return hints.get(topic, '그림의 축·화살표·표 구조를 먼저 읽고 본문 설명과 연결한다.')


def compose_left(text: str, topic: str) -> str:
    bullets = source_bullets(text, 4)
    if not bullets:
        bullets = ['이 페이지의 제목·그림·표가 강의 흐름에서 담당하는 역할을 확인한다.']
    bullet_text = '\n'.join('• ' + b for b in bullets)
    return f'강의자료 핵심\n{bullet_text}\n\n그림 읽기\n• {visual_hint(topic)}'


def compose_right(topic: str) -> str:
    d = TOPICS[topic]
    return (
        '쉽고 자세하게\n' + d['easy'] + '\n\n'
        '관련 개념\n' + d['related'] + '\n\n'
        '심화·연구 확장\n' + d['advanced']
    )


def header(img, section: str, page_no: int):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 47), fill=NAVY2)
    d.text((54, 15), 'ELECTROCHEMISTRY & PEMFC - THREE-LECTURE INTEGRATED STUDY GUIDE', font=F(18, True), fill=WHITE)
    d.line((54, 880, 1545, 880), fill=TEAL, width=3)
    d.text((54, 884), 'Source layers: 85-page electrochemistry handout · 30-page PEMFC handout · three lecture videos · clearly labeled supplementary engineering notes', font=F(12), fill=MUTED)
    d.text((1512, 881), str(page_no), font=F(14, True), fill=NAVY)


def study_page(section: str, number: str, title: str, subtitle: str, source_img: Image.Image, left: str, right: str, key: str, page_no: int) -> Image.Image:
    img = Image.new('RGB', (W, H), WHITE)
    d = ImageDraw.Draw(img)
    header(img, section, page_no)
    d.rectangle((62, 68, 126, 126), fill=TEAL)
    d.text((79, 82), number, font=F(25, True), fill=WHITE)
    d.text((148, 74), title, font=F(31, True), fill=NAVY)
    d.text((64, 130), subtitle, font=F(15), fill=MUTED)
    d.line((64, 154, 1538, 154), fill=TEAL, width=3)

    # Enlarged source slide; no video evidence/time panel.
    frame = (92, 166, 1508, 518)
    rounded(d, frame, fill=WHITE, outline='#B7CCE2', radius=12, width=2)
    fitted = fit_image(source_img, (frame[2]-frame[0]-20, frame[3]-frame[1]-18), WHITE)
    img.paste(fitted, (frame[0]+10, frame[1]+9))

    left_box = (64, 536, 780, 815)
    right_box = (820, 536, 1536, 815)
    rounded(d, left_box, LIGHT_BLUE, outline=BORDER, radius=10, width=2)
    rounded(d, right_box, LIGHT_TEAL, outline=TEAL_DARK, radius=10, width=2)
    d.text((84, 551), 'SOURCE + VISUAL', font=F(18, True), fill=NAVY)
    d.text((840, 551), 'LEARN + CONNECT + EXTEND', font=F(18, True), fill=TEAL_DARK)
    draw_text(d, left, (84, 582, 676, 216), start=17, min_size=13, color=TEXT, leading=1.24)
    draw_text(d, right, (840, 582, 676, 216), start=17, min_size=13, color=TEXT, leading=1.24)

    d.rectangle((64, 825, 1536, 866), fill='#EAF1F8', outline=NAVY, width=2)
    d.rectangle((64, 825, 155, 866), fill=NAVY)
    d.text((87, 836), '핵심', font=F(19, True), fill=WHITE)
    draw_text(d, key, (177, 834, 1338, 26), start=17, min_size=14, color=NAVY, bold=True, leading=1.15)
    return img


def cover_page(page_no: int) -> Image.Image:
    img = Image.new('RGB', (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 180), fill=NAVY2)
    d.rectangle((0, 180, W, 193), fill=TEAL)
    d.text((72, 58), 'HYDROGEN ENERGY EXPERIMENT · ELECTROCHEMISTRY · PEMFC', font=F(24, True), fill='#BFEFF0')
    d.text((72, 230), '전기화학 분석과 PEMFC 이론·실습', font=F(54, True), fill=NAVY)
    d.text((72, 305), '세 강의를 하나의 인과사슬로 연결한 최종 학습서', font=F(34, True), fill=TEAL_DARK)
    d.text((72, 385), '강의 슬라이드 확대 · 쉬운 원리 설명 · 관련/심화 개념 · 실험 SOP · 최신 연구동향', font=F(23), fill=TEXT)
    items = [
        ('전기화학 기반', '전극반응 · potentiostatic/galvanostatic · LSV · EIS'),
        ('동적·정량 분석', 'RDE/RRDE · 전위계단 · Cottrell/Anson · 벌크전해 · dQ/dV'),
        ('PEMFC', '막 · 촉매층 · GDL/MPL · 분리판 · 조립 · 테스트 스테이션'),
        ('연구 확장', 'EIS/DRT · operando 진단 · 저-PGM 촉매 · EMS/PHM · 디지털 트윈'),
    ]
    y = 485
    for i, (a,b) in enumerate(items, 1):
        d.rounded_rectangle((74, y, 1500, y+68), radius=14, fill=LIGHT_BLUE if i%2 else LIGHT_TEAL, outline=TEAL, width=2)
        d.text((98, y+18), f'{i:02d}', font=F(25, True), fill=TEAL_DARK)
        d.text((160, y+13), a, font=F(24, True), fill=NAVY)
        d.text((420, y+16), b, font=F(20), fill=TEXT)
        y += 78
    d.text((72, 830), '학부 고학년 - 대학원 입문 - 연구개발 실무', font=F(21, True), fill=NAVY)
    d.text((1410, 830), 'FINAL', font=F(21, True), fill=TEAL_DARK)
    return img


def info_page(title: str, subtitle: str, blocks: list[tuple[str,str]], key: str, page_no: int) -> Image.Image:
    img = Image.new('RGB', (W, H), WHITE)
    d = ImageDraw.Draw(img)
    header(img, 'START', page_no)
    d.rectangle((62, 68, 126, 126), fill=TEAL)
    d.text((78, 82), '00', font=F(25, True), fill=WHITE)
    d.text((148, 74), title, font=F(31, True), fill=NAVY)
    d.text((64, 130), subtitle, font=F(15), fill=MUTED)
    d.line((64, 154, 1538, 154), fill=TEAL, width=3)
    n = len(blocks)
    cols = 2
    w = 710
    h = 270 if n <= 4 else 205
    positions=[]
    for i in range(n):
        row=i//cols; col=i%cols
        positions.append((64+col*756, 180+row*(h+24), 64+col*756+w, 180+row*(h+24)+h))
    for i, ((head, body), box) in enumerate(zip(blocks, positions)):
        rounded(d, box, LIGHT_BLUE if i%2==0 else LIGHT_TEAL, outline=BORDER if i%2==0 else TEAL_DARK, radius=12, width=2)
        d.text((box[0]+20, box[1]+17), head, font=F(21, True), fill=NAVY if i%2==0 else TEAL_DARK)
        draw_text(d, body, (box[0]+20, box[1]+54, box[2]-box[0]-40, box[3]-box[1]-70), start=18, min_size=13, color=TEXT, leading=1.3)
    d.rectangle((64, 825, 1536, 866), fill='#EAF1F8', outline=NAVY, width=2)
    d.rectangle((64, 825, 155, 866), fill=NAVY)
    d.text((87, 836), '핵심', font=F(19, True), fill=WHITE)
    draw_text(d, key, (177, 834, 1338, 26), start=17, min_size=14, color=NAVY, bold=True, leading=1.15)
    return img


DEEP_DIVES = [
('통합 진단: 분극곡선-CI-EIS-DRT', '한 운전점에서 분극곡선은 총손실, CI는 빠른 오믹 drop, EIS는 주파수별 과정, DRT는 중첩시간의 후보를 제공한다. 서로 다른 운전점의 데이터를 섞지 않고 gas/RH/T/P와 안정화 기준을 고정한다.', 'HFR-Rct-Rmt를 성능·물관리·열화와 연결하되 단일 특징을 고장모드에 일대일 대응시키지 않는다. 압력·가습·stoichiometry perturbation, 셀전압 분포와 outlet water를 함께 사용한다.', '최근에는 online impedance, Bayesian DRT, uncertainty-aware state estimation을 사용해 진단 특징과 신뢰도를 함께 EMS에 전달한다.', '서로 다른 진단기법은 같은 상태와 경계조건에서 결선해야 원인분리가 가능하다.'),
('RDE/RRDE에서 MEA로의 승격 경계', 'RDE는 잘 정의된 액상·회전 유동에서 intrinsic ORR 경향을 비교하는 데 강하다. MEA는 ionomer film, oxygen transport, liquid water, contact와 압축이 추가된다.', 'RDE mass activity가 높아도 H2-air MEA에서 저 Pt loading과 고전류 성능이 낮을 수 있다. catalyst ink, ionomer/carbon ratio, pore accessibility와 AST를 별도로 검증한다.', '2025-2026 연구는 ordered PtCo intermetallic, carbon-shell protection, mesoporous support로 저-PGM 활성·내구의 동시 개선을 시도한다.', 'Half-cell 결과는 MEA 성능·내구·수송 검증을 거친 뒤에만 시스템 성능으로 승격한다.'),
('EIS/DRT의 비식별성과 불확도', '같은 EIS 곡선을 여러 ECM이 비슷하게 맞출 수 있고, DRT peak도 정칙화·주파수범위·noise에 따라 달라진다.', '회로 최소성, residual, parameter correlation, profile likelihood와 perturbation consistency를 함께 본다. DRT는 peak 수를 물리과정 수로 자동 해석하지 않는다.', '2025 연구는 DRT의 사용자 선택 의존성을 경고하면서 Bayesian mixture와 frequency-band 기반 정칙화 선택으로 자동화·불확도 정량화를 추진한다.', '모델의 예쁜 적합보다 대안모델과 불확도를 공개하는 것이 재현 가능한 해석이다.'),
('PEMFC 물관리의 안전운전창', '저습에서는 막전도도 저하와 HFR 증가, 과습에서는 cathode/GDL 수송저항과 변동 증가가 나타난다. 두 현상은 동시에 다른 위치에서 발생할 수 있다.', '전류, 온도, inlet dew point, pressure, stoichiometry, outlet humidity와 pressure drop을 물수지로 연결한다. 단일 RH 값보다 막·촉매층·GDL의 공간분포가 중요하다.', 'Operando neutron/X-ray imaging, segmented cell과 digital twin은 local water saturation과 current/temperature 분포를 결합한다.', 'Dry-out과 flooding 사이의 좁은 운전창을 상태추정과 제어제약으로 관리한다.'),
('2025-2026 저-PGM 촉매 연구동향', 'Ordered PtCo는 Pt skin과 규칙구조를 통해 ORR activity와 Co dissolution 안정성을 개선하려 한다. carbon shell과 N-C support는 입자·금속용출을 억제한다.', '최근 보고들은 ultralow Pt loading의 H2-air 성능과 60,000-150,000 cycle 내구를 강조한다. 숫자는 MEA 면적·loading·가스·보정조건을 함께 비교해야 한다.', '대표 문헌: ACS Sustainable Chem. Eng. 2025, DOI 10.1021/acssuschemeng.5c06575; Adv. Energy Mater. 2026, DOI 10.1002/aenm.202506060; Adv. Mater. 2026, DOI 10.1002/adma.202510847.', '촉매 연구의 기준은 RDE peak activity가 아니라 저-loading MEA의 성능·수송·내구 동시검증이다.'),
('막·ionomer 연구동향', '막과 catalyst-layer ionomer는 같은 PFSA라도 역할과 최적 구조가 다르다. 막은 bulk proton conduction·crossover·내구, ionomer film은 O2 transport와 Pt 접근성을 좌우한다.', '초박막·강화 PFSA, hydrocarbon membrane, 고온용 PBI계, radical scavenger와 저-EW ionomer가 주요 방향이다. 기계·화학 열화와 swelling을 함께 본다.', '계면연구는 ionomer film thickness, local water activity, Pt/ionomer interaction과 oxygen permeability를 nm-scale 분석·모델과 연결한다.', '막 저항을 낮추는 설계가 항상 촉매층 산소수송과 내구에 유리한 것은 아니다.'),
('GDL/MPL·유로의 operando 연구동향', 'GDL/MPL과 유로는 물을 무조건 배출하는 부품이 아니라 gas access와 membrane hydration을 균형화하는 수송계다.', 'Tomography, X-ray/neutron imaging, pore-network model로 rib/channel 아래 saturation, droplet breakthrough와 oxygen resistance를 추적한다.', 'Graded porosity·wettability, MPL crack engineering, topology-optimized flow field와 압축 공동최적화가 활발하다.', 'GDL과 유로는 독립부품이 아니라 압축·운전 RH·유량과 함께 설계한다.'),
('스택 압축·접촉·제조 variation', '셀 성능분산은 재료 차이뿐 아니라 gasket 두께, plate flatness, bolt preload와 GDL 압축분포에서 생긴다.', '누설률, contact resistance, pressure-sensitive film, 셀전압·온도 분포를 lot/조립순서와 연결한다. torque-only 관리의 한계를 인식한다.', 'Digital manufacturing은 공정센서·CT/vision 검사·serial-level traceability를 활용해 초기불량과 장기열화를 예측한다.', '조립 메타데이터를 전기화학 데이터와 결합해야 스택 수준 원인규명이 가능하다.'),
('테스트 스테이션 자동화와 데이터 provenance', '시험 recipe, calibration, sensor 위치, gas purity, dew point와 line temperature를 version-controlled metadata로 저장한다.', 'raw command/measured waveform, overload·interlock·range flag, 제외이유를 보존한다. 처리 결과는 source hash와 code commit으로 원자료까지 역추적한다.', '자동화 추세는 online EIS, adaptive test design, anomaly detection이지만 fail-safe와 물리 sanity gate가 우선이다.', '좋은 데이터는 그래프보다 원자료-조건-처리-결론의 추적사슬이 닫힌 데이터다.'),
('Health-conscious MPC와 EMS/PHM', '연료전지-배터리 하이브리드는 수소소비만 최소화하면 열화가 배터리·연료전지 중 한쪽으로 전가될 수 있다.', '목적함수에 H2, battery throughput/temperature, FC ramp·저전압·RH/air constraint, terminal SOC를 포함한다. gross/net power와 보조기기 경계를 선언한다.', '2025 health-conscious MPC 연구는 cathode catalyst degradation을 물리모델에 포함하고 current·H2/air flow·dew point를 공동최적화한다(10.1016/j.ifacol.2025.07.084).', '진단특징은 상태·불확도·freshness와 함께 제약으로 전달할 때 제어에 안전하게 사용된다.'),
('AI·physics-informed 진단', 'AI는 EIS·분극·센서 패턴의 복잡한 상관을 학습할 수 있지만 운전조건 shift와 센서 drift에 취약하다.', '학습/검증 분할을 셀·운전조건·시간축 기준으로 설계하고, leakage와 OOD를 막는다. 물리보존·단조성·단위계약을 모델 구조나 loss에 넣는다.', 'Bayesian/ensemble uncertainty, domain adaptation, active learning과 digital twin residual을 결합하는 방향이 확대되고 있다.', '정확도 하나보다 범위 밖 입력을 감지하고 보수적으로 제약을 갱신하는 능력이 중요하다.'),
('연구설계 매트릭스', '질문-입력-관측-추정-독립검증-실패조건을 한 표로 작성하면 실험과 논문의 주장범위가 명확해진다.', '예: 물관리 질문에는 RH/flow/pressure perturbation, HFR·저주파 EIS·outlet water·cell distribution, imaging/물수지 검증이 필요하다.', '새로움은 AI 사용 자체가 아니라 정보구조, 제약, 검증환경, 반례와 uncertainty handling에서 나온다.', '논문 주장은 측정과 모델이 실제로 구속한 범위까지만 확장한다.'),
]


def deep_page(item, idx, page_no):
    title, easy, related, advanced, key = item
    blocks=[('쉽고 자세하게',easy),('관련 개념과 연결',related),('최신 연구동향',advanced),('실험·논문에 적용',key+'\n\n권장 산출물: 원자료·조건표·검증그래프·불확도·반례·source hash.')]
    return info_page(f'DEEP DIVE {idx:02d} · {title}', '강의 밖 보충이지만 각 슬라이드의 개념을 연구수준으로 연결하는 확장 학습', blocks, key, page_no)


def references_pages(start_no: int):
    refs = [
        ('기초 전기화학·연료전지', 'A. J. Bard and L. R. Faulkner, Electrochemical Methods, 2nd ed.\nM. E. Orazem and B. Tribollet, Electrochemical Impedance Spectroscopy, 2nd ed.\nR. O’Hayre et al., Fuel Cell Fundamentals, 3rd ed.\nV. G. Levich, Physicochemical Hydrodynamics.'),
        ('2025-2026 촉매·DRT', 'Ordered PtCo + protective layer: 10.1021/acssuschemeng.5c06575\nPtCo/Co-N-C ultralow Pt: 10.1002/aenm.202506060\nDurable ordered Pt3Co: 10.1002/adma.202510847\nDRT limitations: 10.1149/1945-7111/adecc8\nBayesian DRT: 10.1021/acs.jpcc.5c04766\nOptimal regularization: 10.1149/1945-7111/adb5c6'),
        ('제어·배터리·방법론', 'Health-conscious PEMFC MPC: 10.1016/j.ifacol.2025.07.084\nML-warm-start thermal MPC: SAE 2025-01-7071\nDifferential analysis of Li-ion cycle data: 10.1021/acs.chemmater.2c01976\nLi-ion degradation review: 10.1039/D1CP00359C\nReliable CV capacitance protocol: 10.1088/2515-7655/abee33'),
        ('근거 범위', '직접 근거: 사용자가 제공한 85쪽 전기화학 강의자료와 30쪽 PEMFC 강의자료.\n음성 근거: AccurateScribe에서 Video Project와 PEMFC 영상의 completed 상태 및 반환된 transcript preview를 확인.\n260907 영상은 AccurateScribe 목록에 노출되지 않아 문장별 verbatim 전사를 주장하지 않음.\n본문은 강의자료·확인된 강의구조와 보충 공학지식을 구분해 구성.'),
    ]
    p1=info_page('참고문헌과 근거 1/2','교재·방법론·최근 연구의 출처',refs[:2], '식과 원리는 표준 교재로, 최신동향은 2025-2026 원 논문으로 교차검증했다.', start_no)
    p2=info_page('참고문헌과 근거 2/2','제어·배터리·음성/자료 검증범위',refs[2:], '정확한 음성 직접인용은 도구가 실제로 반환한 범위 안에서만 인정한다.', start_no+1)
    return [p1,p2]


def save(img: Image.Image, idx: int):
    OUT.mkdir(parents=True, exist_ok=True)
    path=OUT/f'slide{idx:03d}.jpg'
    img.save(path,'JPEG',quality=91,optimize=True,progressive=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('slide*.jpg'):
        old.unlink()
    electro=fitz.open(SRC/'electrochemistry.pdf')
    pemfc=fitz.open(SRC/'pemfc.pdf')
    page_no=1
    save(cover_page(page_no),page_no); page_no+=1
    save(info_page('학습 로드맵','세 강의를 암기목록이 아니라 하나의 물리·실험·진단 체계로 읽는다.',[
        ('1회독 · 구조','원 슬라이드와 하단 핵심을 따라 전기화학 입력-응답, PEMFC 층과 수송경로를 잡는다.'),
        ('2회독 · 원리','평형-kinetics-transport, 막 수화-촉매반응-GDL/유로를 수식과 그래프로 연결한다.'),
        ('3회독 · 실험','SOP·단위·부호·장비대역폭·안전·데이터 QA를 실제 시험계획서로 바꾼다.'),
        ('4회독 · 연구','최신 촉매·operando·EIS/DRT·EMS/PHM 동향에서 연구질문과 검증사슬을 설계한다.')],
        '항상 무엇을 제어했고, 무엇이 이동했으며, 무엇을 측정해 어떤 가정으로 추정했는지 묻는다.',page_no),page_no); page_no+=1
    save(info_page('자료 통합과 검증범위','세 영상의 음성·강의자료·보충설명을 같은 근거수준으로 섞지 않는다.',[
        ('강의자료','85쪽 기초 전기화학 분석과 30쪽 PEMFC 이론·실습 자료를 전 페이지 반영했다.'),
        ('AccurateScribe','Video Project와 PEMFC 영상은 completed로 확인됐고 반환 transcript preview를 기술용어와 대조했다.'),
        ('영상 260907','AccurateScribe 목록에 노출되지 않아 문장별 인용은 만들지 않고, 강의자료와 기존 시각 정합 결과로 내용구조를 반영했다.'),
        ('보충계층','관련·심화 개념과 2025-2026 연구동향은 별도 보충설명으로 구분하며 원 강의 발언처럼 표현하지 않는다.')],
        '자료가 직접 지지하는 내용과 보충 공학지식을 분리해야 자세하면서도 신뢰할 수 있다.',page_no),page_no); page_no+=1
    save(info_page('전체 개념 지도','전기화학 측정에서 PEMFC 시스템·진단·제어까지 연결한다.',[
        ('CONTROL','전위·전류·회전속도·가스·RH·온도·압력·부하를 정의한다.'),
        ('TRANSPORT','전자·이온·기체·물·열의 이동경로와 경계조건을 모델링한다.'),
        ('INTERFACE','전하전달·흡착·이중층·촉매층·막 계면에서 반응이 일어난다.'),
        ('MEASURE → INFER','I-V-t, EIS, Q, dQ/dV에서 물성·상태·열화와 불확도를 추정한다.')],
        '곡선은 결과다. 입력과 전달경로를 먼저 보면 처음 보는 데이터도 원인에서 읽을 수 있다.',page_no),page_no); page_no+=1

    # 85 electrochemistry pages
    for i in range(len(electro)):
        text, source_img=extract_page(electro,i)
        p=i+1
        topic=topic_for('electro',p,text)
        title=title_from_text(text,p,'전기화학')
        left=compose_left(text,topic)
        right=compose_right(topic)
        subtitle=f'기초 전기화학 분석 강의자료 p.{p} · 음성/영상 구조와 통합 해설'
        save(study_page('ELECTROCHEMISTRY',f'{p:02d}',title,subtitle,source_img,left,right,TOPICS[topic]['key'],page_no),page_no)
        page_no+=1

    save(info_page('전기화학 → PEMFC 연결 지도','분석기법을 실제 PEMFC 부품·운전·고장모드에 연결한다.',[
        ('분극곡선','활성화-오믹-수송 손실을 전체 셀 성능으로 관찰한다.'),
        ('Current interrupt','즉시 전압강하와 느린 회복을 분리해 오믹·동특성을 본다.'),
        ('EIS/DRT','HFR·전하전달·기체/물수송의 시간척도 후보를 분리한다.'),
        ('부품·운전','막·촉매층·GDL/MPL·유로·압축과 RH/T/P/stoichiometry를 교차검증한다.')],
        '분석특징은 부품·운전조건·측정유효성과 함께 해석해야 고장진단이 된다.',page_no),page_no); page_no+=1

    # 30 PEMFC pages
    for i in range(len(pemfc)):
        text, source_img=extract_page(pemfc,i)
        p=i+1
        topic=topic_for('pemfc',p,text)
        title=title_from_text(text,p,'PEMFC')
        left=compose_left(text,topic)
        right=compose_right(topic)
        subtitle=f'PEMFC 이론 및 실험 실습 기초 강의자료 p.{p} · 구조-수송-실험 연결 해설'
        save(study_page('PEMFC',f'{p:02d}',title,subtitle,source_img,left,right,TOPICS[topic]['key'],page_no),page_no)
        page_no+=1

    save(info_page('최신 연구동향 학습법','아래 확장 장은 원 강의의 개념을 2025-2026 연구질문으로 연결한다.',[
        ('재료','저-PGM ordered intermetallic, 막/ionomer, GDL/MPL와 분리판의 trade-off를 본다.'),
        ('진단','operando imaging, online EIS, DRT와 uncertainty-aware state estimation을 연결한다.'),
        ('시스템','열·공기·수소·습도·배터리를 degradation-aware MPC/EMS로 공동관리한다.'),
        ('연구설계','새 방법보다 반례·불확도·독립검증·재현 가능한 processing receipt를 우선한다.')],
        '최신성은 알고리즘 이름이 아니라 물리적 제약과 엄격한 검증구조에서 나온다.',page_no),page_no); page_no+=1
    for idx,item in enumerate(DEEP_DIVES,1):
        save(deep_page(item,idx,page_no),page_no); page_no+=1
    for im in references_pages(page_no):
        save(im,page_no); page_no+=1

    manifest={'page_count':page_no-1,'files':[f'study_guide_final_pages/slide{i:03d}.jpg' for i in range(1,page_no)]}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))

if __name__=='__main__':
    main()
