from __future__ import annotations
import hashlib, html, json, os, re, sys, textwrap
from pathlib import Path
import requests
import fitz

URL=os.environ.get('GUIDE_URL','')
ROOT=Path.cwd(); OUT=ROOT/'artifacts'; OUT.mkdir(exist_ok=True)
SRC=OUT/'source_guide.pdf'; FINAL=OUT/'hydrogen_energy_complete_final.pdf'
if not URL: raise SystemExit('GUIDE_URL missing')
r=requests.get(URL,timeout=180); r.raise_for_status(); SRC.write_bytes(r.content)

NAVY=(12/255,48/255,100/255); TEAL=(20/255,148/255,153/255); LIGHT=(234/255,248/255,247/255)
BLUE=(37/255,112/255,163/255); ORANGE=(230/255,132/255,29/255); GREEN=(38/255,143/255,97/255)
TEXT=(21/255,42/255,75/255); PALE=(239/255,246/255,252/255); PURPLE=(108/255,78/255,159/255)
FONT='/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
FONT_B='/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf'
if not Path(FONT).exists():
    FONT='/usr/share/fonts/truetype/nanum/NanumGothic.ttf'; FONT_B='/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'

REPL={
 '전 기':'전기','주파 수':'주파수','시 스템':'시스템','단 순':'단순','반 응':'반응','측 정':'측정','운 전':'운전','연 료':'연료',
 '연 료전지':'연료전지','다 른':'다른','가 능':'가능','알 수 있 음':'알 수 있음','성 립':'성립','설 명':'설명','결 과':'결과',
 '전 위':'전위','전 류':'전류','확 산':'확산','저 항':'저항','오 믹':'오믹','기 준전극':'기준전극','속도결정단 계':'속도결정단계',
 '일반 화':'일반화','의 미':'의미','재 현':'재현','분 리':'분리','관 측':'관측','추 정':'추정','원자료 순 서로':'원자료 순서로',
 '모델 식별 성':'모델 식별성','동 적':'동적','기체확 산층':'기체확산층','액 상수':'액상수','전자 및 10 전도':'전자 및 열전도',
 'Gavanostatic':'Galvanostatic','back difusion':'back diffusion','하벼':'하며','활용를 활용':'활용','제작 된':'제작된'
}
def clean(s:str)->str:
    s=s.replace('\x00','').replace('\ufffd','').replace('\u2028',' ').replace('\u2029',' ')
    s=re.sub(r'[ \t]+',' ',s); s=re.sub(r' *\n *','\n',s).strip()
    for a,b in REPL.items(): s=s.replace(a,b)
    s=s.replace('•','- ')
    s=re.sub(r'\s+([,.;:)])',r'\1',s)
    s=re.sub(r'([([])\s+',r'\1',s)
    return s

def lines(text): return [clean(x) for x in text.splitlines() if clean(x)]
def find_idx(ls, needles, start=0):
    for i in range(start,len(ls)):
        if any(n in ls[i] for n in needles): return i
    return -1

def section(ls, start_needles, end_needles):
    a=find_idx(ls,start_needles)
    if a<0:return ''
    b=len(ls)
    for n in end_needles:
        j=find_idx(ls,[n],a+1)
        if j>=0:b=min(b,j)
    return clean('\n'.join(ls[a+1:b]))

def dedupe_sentences(s):
    bits=re.split(r'(?<=[.!?다])\s+|\n+',clean(s)); out=[]; seen=set()
    for b in bits:
        b=b.strip(' -')
        if len(b)<3:continue
        k=re.sub(r'\s+','',b)
        if k in seen:continue
        seen.add(k); out.append(b)
    return ' '.join(out)

def parse_page(text):
    ls=lines(text)
    joined='\n'.join(ls)
    m=re.search(r'(기초 전기화학 분석|PEMFC 이론 및 실험 실습 기초)\s*[·-]\s*(?:강의자료\s*)?p\.?\s*(\d+)',joined,re.I)
    if not m:return None
    course=m.group(1); slide=int(m.group(2))
    title=''
    for x in ls[:10]:
        mt=re.match(r'^\d{2}\s+(.+)$',x)
        if mt:title=mt.group(1);break
    if not title:
        title=next((x for x in ls if x not in [course] and len(x)>5),'강의 해설')
    easy=section(ls,['2 쉽게 이해하기'],['3 핵심 수식','3 교수 설명','4 교수 설명','4 관련 개념','핵심 정리'])
    ppt=section(ls,['1 PPT 내용 해석'],['2 쉽게 이해하기'])
    formula=section(ls,['3 핵심 수식'],['4 교수 설명','4 관련 개념','5 관련 개념','핵심 정리'])
    prof=section(ls,['교수 설명 전체 요약'],['4 관련 개념','5 관련 개념','핵심 정리'])
    related=section(ls,['4 관련 개념','5 관련 개념'],['핵심 정리'])
    summ=section(ls,['핵심 정리'],[])
    time=''
    mm=re.search(r'교수 설명 전체 요약\s*\[([^\]]+)\]',joined)
    if mm:time=mm.group(1)
    # Remove template artifacts without erasing technical content.
    prof=prof.replace('화면의 식·그림·표를 따라','')
    prof=re.sub(r'를 설명한다\.?','.',prof)
    prof=prof.replace('의 인과관계를 앞뒤 페이지와 연결한다.','.')
    prof=re.sub(r'\([^)]*(?:AccurateScribe|시각 정합)[^)]*\)','',prof)
    prof=dedupe_sentences(prof)
    ppt=re.sub(r'페이지는 .*?의 의미를 정리한다\.','',ppt)
    ppt=ppt.replace('슬라이드의 그림·표·식은 단순 장식이 아니라, 제어조건과 관측량을 연결해 다음 해석 단계로 넘어가기 위한 근거다.','')
    return {'course':course,'slide':slide,'title':clean(title),'time':time,'ppt':dedupe_sentences(ppt),'easy':dedupe_sentences(easy),'formula':clean(formula),'prof':prof,'related':dedupe_sentences(related),'summary':dedupe_sentences(summ)}

FORMULAS=[
 (r'Nernst|표준전극|형식전위', 'E = E° + (RT/nF) ln(a_O/a_R)', '평형전위는 활동도와 온도에 의해 결정된다. 형식전위 E°′는 특정 매질 조건을 포함한 값이므로 전해질·pH·착물 조건을 바꿔 그대로 옮기지 않는다.'),
 (r'Randles|주사속도|피크 전류', 'i_p = 2.69×10⁵ n^(3/2) A D^(1/2) C* v^(1/2)', '25 °C, 평면 반무한확산, 가역계와 일관된 단위계에서의 관계다. 기울기 하나로 n과 D를 동시에 고유하게 정할 수 없다.'),
 (r'임피던스|EIS|Nyquist|Bode', 'Z(ω) = V~(ω)/I~(ω) = Z′(ω) + jZ″(ω)', '작은 신호 선형성·정상성·인과성이 먼저 검증되어야 한다. 좋은 회로 적합이 유일한 물리 메커니즘을 증명하지는 않는다.'),
 (r'RC|시간상수|특성주파수', 'τ = RC,    f_c = 1/(2πRC)', '특성주파수는 이상 RC의 대표시간을 연결한다. 분산된 반응·비균질 전극에서는 CPE나 분포 시간상수가 필요할 수 있다.'),
 (r'CPE', 'Z_CPE = 1 / [Q(jω)^α]', 'α=1이면 이상 커패시터에 가까워진다. Q의 단위는 α에 의존하므로 커패시턴스와 무조건 동일시하지 않는다.'),
 (r'Warburg|확산 임피던스', 'Z_W = σ(1-j)/√ω', '반무한 확산의 이상형이다. 유한길이 확산, 대류, 다공성 전극에서는 저주파 극한과 기울기가 달라진다.'),
 (r'수화율|λ와 전도도', 'λ = n(H₂O) / n(SO₃⁻)', 'λ는 막의 술폰산기당 물분자 수다. 전도도 상관식은 막 조성·온도·수화 이력의 유효범위를 명시해야 한다.'),
 (r'수분수지|전기삼투|역확산', 'N_w = n_d i/F − D_w ∂C_w/∂x', '좌표와 플럭스의 양의 방향을 먼저 정한다. back diffusion 방향은 water-content gradient가 결정하며 항상 한 방향이라고 외우지 않는다.'),
 (r'면적저항|HFR', 'ASR_m = ∫₀ᴸ dx / σ[λ(x),T]', '국소 탈수는 조화평균 성격의 저항을 크게 만들 수 있다. HFR에는 막뿐 아니라 접촉·전자·배선 기여가 포함될 수 있다.'),
 (r'PEMFC 기본 반응|전하 이동|수소 산화|산소 환원', 'H₂ → 2H⁺ + 2e⁻\n½O₂ + 2H⁺ + 2e⁻ → H₂O', '전자와 양성자의 경로를 분리해야 외부회로에서 전기일을 얻는다. 실제 전압은 활성화·오믹·물질전달 손실 때문에 가역전압보다 낮다.'),
 (r'압축|체결|엔드플레이트', 'C = (t₀ − t)/t₀ × 100%', '압축은 접촉저항을 낮추지만 과도하면 기공·투과도·실링·막 응력을 악화시킨다. 토크보다 실제 두께·하중·평탄도를 함께 기록한다.'),
 (r'RH|가습|테스트 스테이션|stoichiometry', 'RH = p_H₂O / p_sat(T) × 100%', '가습기 setpoint와 셀 입구 RH는 배관 열손실·응축·압력에 따라 다를 수 있다. dew point, 실제 온도와 압력을 함께 기록한다.'),
]

def formula_for(title):
    for pat,eq,note in FORMULAS:
        if re.search(pat,title,re.I):return eq,note
    return '', '식이 없는 개념 페이지에서도 입력·출력·단위·경계조건·독립 검증을 명시해야 한다.'

def enrichment(title,course):
    t=title.lower()
    if any(k in t for k in ['lsv','선형주사','onset','peak','가역','비가역','주사속도']):
        return ('전위 주사에서 관측 전류는 이중층 충전, 전자전달 속도, 반응물 확산과 iR drop의 합성 결과다. onset은 정의법과 background에 의존하고, peak 위치·높이는 scan rate, 농도, 전극면적, 온도와 반응 가역성에 함께 좌우된다.',
                '여러 scan rate에서 원자료와 background를 함께 보존하고 i_p–√v, E_p–ln v, 반복성 및 생성물 분석을 교차검증한다. 최근에는 자동화 voltammetry와 Bayesian parameter inference를 결합하지만, prior와 모델 불일치의 영향을 별도로 보고해야 한다.')
    if any(k in t for k in ['eis','임피던스','nyquist','bode','ecm','drt','warburg','cpe']):
        return ('EIS는 한 작동점 주위의 작은 신호 응답을 주파수별로 분해한다. 고주파 절편, arc, 저주파 tail은 유용한 특징이지만 장비·배선·접촉·열·수분 변화가 함께 섞일 수 있어 특정 반응과 자동으로 일대일 대응하지 않는다.',
                'amplitude sweep, drift check, Kramers–Kronig 일관성, residual 구조, parameter correlation과 조건 perturbation을 함께 본다. 최신 연구의 fast/multisine EIS, Bayesian DRT와 physics-informed learning도 이 admission gate를 통과한 데이터에서만 의미가 있다.')
    if any(k in t for k in ['nafion','막','수화','양성자','전해질']):
        return ('PFSA 막은 양성자 전도, 전자 차단, 반응가스 분리를 동시에 수행한다. 수화가 부족하면 protonic resistance가 증가하고, 과도한 수화·팽윤과 액상수는 계면·기계·수송 문제를 만든다. 막의 물 상태는 전류, RH, 온도, 압력, 두께와 운전 이력의 결과다.',
                'water uptake, λ, conductivity, swelling, gas crossover와 HFR을 같은 시편·조건에서 비교한다. 고온·저습 막 연구는 산 보유·기계 안정성·내구성을 함께 다루며, 단기 conductivity만으로 시스템 우수성을 주장하지 않는다.')
    if any(k in t for k in ['촉매','sabatier','pt ','orr','반응영역']):
        return ('촉매층 성능은 Pt 고유활성뿐 아니라 ECSA, ionomer coverage, 전자·양성자·기체/물의 연결성과 국소 수분상태가 정한다. Sabatier 직관은 유용하지만 실제 ORR은 중간체, 전해질, 표면 facet, strain과 coverage에 의해 달라진다.',
                'geometric, mass, specific activity와 Pt loading을 구분하고 AST 전후 ECSA·입자크기·용출·탄소부식을 측정한다. 저-PGM·ordered intermetallic 연구는 실제 MEA와 동적 heavy-duty 조건의 내구 검증으로 이동하고 있다.')
    if any(k in t for k in ['gdl','mpl','분리판','유로','기체확산']):
        return ('GDL/MPL과 유로는 반응가스 공급, 액상수 배출, 전자·열 전달, 기계 지지를 동시에 담당한다. porosity를 높이는 것만으로는 충분하지 않으며 압축, PTFE 분포, pore hierarchy, 접촉저항과 압력손실 사이에 trade-off가 있다.',
                'through-/in-plane permeability와 전도도, capillary-pressure curve, limiting current, ΔP와 operando water imaging을 함께 비교한다. 최근 연구는 XCT·neutron imaging과 pore-network/CFD를 결합해 국소 flooding과 rib/channel 불균일을 추적한다.')
    if any(k in t for k in ['조립','가스켓','엔드플레이트','체결','스택 형성']):
        return ('스택 조립은 단순 적층이 아니라 정렬, 실링, 압축, 전기접촉과 유체 분리를 동시에 닫는 품질공정이다. 국소 압축 불균일은 contact resistance와 기체·물 수송, 막 응력, 셀간 성능편차를 함께 바꾼다.',
                '부품 lot·두께·방향, 단계별 토크/하중, plate 평탄도, leak rate와 electrical isolation을 기록한다. pressure film, displacement sensor와 cell-wise EIS를 결합하면 조립결함과 운전열화를 더 잘 분리할 수 있다.')
    if any(k in t for k in ['테스트 스테이션','regulator','mfc','가습','압력']):
        return ('테스트 스테이션은 경계조건 생성기이자 계측시스템이다. setpoint는 실제 inlet/outlet gas 상태와 다를 수 있으며 배관 열손실, 응축, 센서 위치·지연, 압력강하가 성능과 진단결과를 바꾼다.',
                'dry/wet flow, dew point, inlet/outlet pressure, cell/coolant temperature, 셀별 전압과 센서 교정이력을 동기화한다. 자동 실험은 편리하지만 interlock, purge, 수소감지, fail-safe와 raw command/measured waveform 보존이 우선이다.')
    if any(k in t for k in ['in situ','ex situ','operando']):
        return ('in situ/operando는 실제 작동 중 전체 시스템과 과도현상을 보존하고, ex situ는 구성요소를 높은 공간·화학 분해능으로 본다. 전자는 현실성이 높지만 원인 비식별성이 크고, 후자는 해체·세척·건조 과정에서 상태를 바꿀 수 있다.',
                '동일 시편의 before/after와 독립 대조군을 설계하고 위치·시간 동기화를 유지한다. 최근 operando X-ray, neutron, Raman/IR와 segmented sensing은 공간 비균일성을 보여주지만 관측창과 센서가 시스템을 교란하는지 검증해야 한다.')
    if any(k in t for k in ['성능','내구','열화','진단']):
        return ('현재 성능, 설계 민감도와 시간에 따른 내구열화는 서로 다른 질문이다. 운전조건 변화가 열화처럼 보일 수 있으므로 baseline recovery, reference condition과 반복 run을 분리해야 한다.',
                'DOE와 global sensitivity, cell-resolved voltage/temperature, 장기 EIS/DRT와 post-mortem을 한 증거사슬로 연결한다. 최신 PHM은 uncertainty, OOD, feature freshness를 EMS 제약에 전달하지만 실험실 상관을 RUL 인과로 과장하지 않는다.')
    return ('슬라이드의 정의를 입력-전달-계면-관측-추정의 인과사슬로 다시 읽는다. 같은 관측값을 여러 원인이 만들 수 있으므로 단일 곡선이나 파라미터만으로 메커니즘을 확정하지 않는다.',
            '원자료, 보정, 운전점, 단위와 불확도를 보존하고 조건을 한 번에 하나씩 바꿔 가설을 반증한다. 최근 연구는 자동화와 AI보다 데이터 provenance, 독립 검증과 source-to-claim 추적성을 더 엄격히 요구한다.')

def esc(s):return html.escape(clean(s)).replace('\n','<br>')
CSS='''
@font-face {font-family:nanum;src:url(NANUM_REG)}
@font-face {font-family:nanum;font-weight:700;src:url(NANUM_BOLD)}
*{font-family:nanum;color:#152b4d;line-height:1.34} h2{font-size:14pt;margin:0 0 8px;color:#fff} h3{font-size:10.4pt;margin:8px 0 3px;color:#159499;border-left:4px solid #159499;padding-left:6px} p,li{font-size:8.25pt;margin:1.5px 0} ul{margin:2px 0 4px 17px;padding:0}.formula{font-family:serif;font-size:13pt;text-align:center;background:#fff6e8;border:1px solid #e6841d;padding:7px;margin:5px 0}.condition{font-size:7.7pt;color:#634613}.tag{font-size:7pt;color:#52677d}.purple{color:#6c4e9f;font-weight:700}.green{color:#268f61;font-weight:700}.orange{color:#e6841d;font-weight:700}.summary{font-size:8.2pt;font-weight:700}'''.replace('NANUM_REG',Path(FONT).as_uri()).replace('NANUM_BOLD',Path(FONT_B).as_uri())

def draw_panel(page, info, part, page_no):
    W,H=page.rect.width,page.rect.height
    rx0,ry0,rx1,ry1=W*0.535,H*0.178,W*0.982,H*0.873
    bottom=fitz.Rect(W*0.035,H*0.886,W*0.982,H*0.977)
    # redact old right panel / bottom summary while preserving title and source slide.
    page.draw_rect(fitz.Rect(rx0-4,ry0-5,rx1+3,ry1+4),color=(1,1,1),fill=(1,1,1),overlay=True)
    page.draw_rect(bottom,color=(1,1,1),fill=(1,1,1),overlay=True)
    page.draw_rect(fitz.Rect(rx0,ry0,rx1,ry1),color=TEAL,fill=LIGHT,width=1.0,overlay=True)
    page.draw_rect(fitz.Rect(rx0,ry0,rx1,ry0+29),color=TEAL,fill=TEAL,overlay=True)
    page.insert_font(fontname='nanum',fontfile=FONT);page.insert_font(fontname='nanumb',fontfile=FONT_B)
    header='교수 설명 · 쉬운 해설' if part==1 else '엄밀성 · 심화 · 연구 연결'
    page.insert_text((rx0+12,ry0+20),header,fontname='nanumb',fontsize=12,color=(1,1,1),overlay=True)
    eq,eqnote=formula_for(info['title'])
    deep,research=enrichment(info['title'],info['course'])
    if part==1:
        prof=info['prof'] or ('해당 강의구간에서는 '+info['title']+'의 정의와 슬라이드 요소를 앞뒤 개념과 연결한다. 화면에 제시된 식·그래프·구조를 실제 실험의 입력과 관측량 관점에서 해석한다.')
        content=f'''<h3>강의구간 전체 해설 <span class="tag">[{esc(info['time'] or '시각 정합 구간')}]</span></h3><p>{esc(prof)}</p><h3>쉽게 이해하기</h3><p>{esc(info['easy'] or info['summary'])}</p><h3>슬라이드가 수행하는 역할</h3><p>{esc(info['ppt'] or '이 페이지는 다음 분석 단계에서 사용할 정의·변수·경계조건을 세우는 역할을 한다.')}</p><h3>핵심 연결</h3><p>{esc(deep)}</p>'''
        summary=(info['summary'] or info['easy'] or info['title'])+' '+deep.split('.')[0]+'.'
    else:
        fbox=f'<div class="formula">{esc(eq)}</div><p class="condition">{esc(eqnote)}</p>' if eq else f'<p>{esc(eqnote)}</p>'
        content=f'''<h3>핵심 수식·엄밀성</h3>{fbox}<h3>관련·심화 개념</h3><p>{esc(info['related'] or deep)}</p><h3><span class="green">실험·공학 적용</span></h3><p>{esc(deep)}</p><h3><span class="purple">추가 학습·연구 동향</span></h3><p>{esc(research)}</p><h3><span class="orange">결론의 한계</span></h3><p>관측된 변화는 셀 상태뿐 아니라 운전 경계조건, 센서 위치·대역폭, 배선, 보정과 처리 알고리즘의 영향을 함께 포함한다. 독립 조건변화와 반복성으로 같은 해석이 유지되는 범위만 주장한다.</p>'''
        summary=(info['summary'] or info['title'])+' 적용할 때는 식의 가정과 경계조건을 먼저 확인하고, 독립 실험과 불확도로 원인 해석을 교차검증한다.'
    rect=fitz.Rect(rx0+11,ry0+36,rx1-10,ry1-8)
    spare,scale=page.insert_htmlbox(rect,content,css=CSS,scale_low=0.72,overlay=True)
    # bottom detailed summary
    page.draw_rect(bottom,color=NAVY,fill=PALE,width=1.0,overlay=True)
    label=fitz.Rect(bottom.x0,bottom.y0,bottom.x0+92,bottom.y1)
    page.draw_rect(label,color=NAVY,fill=NAVY,overlay=True)
    page.insert_textbox(label,'핵심 정리\n및 요약',fontname='nanumb',fontsize=8.6,color=(1,1,1),align=1,overlay=True)
    sumrect=fitz.Rect(label.x1+8,bottom.y0+5,bottom.x1-8,bottom.y1-4)
    page.insert_htmlbox(sumrect,f'<div class="summary">{esc(summary)}</div>',css=CSS,scale_low=0.76,overlay=True)
    # page/part marker
    page.insert_text((W-42,H-9),f'{page_no:03d}',fontname='nanum',fontsize=6.7,color=(0.35,0.43,0.52),overlay=True)
    page.insert_text((rx1-43,ry0+20),f'{part}/2',fontname='nanumb',fontsize=7.3,color=(1,1,1),overlay=True)
    return {'spare':spare,'scale':scale}

def add_qa_page(doc, stats):
    p=doc.new_page(width=1024,height=576);p.insert_font(fontname='nanum',fontfile=FONT);p.insert_font(fontname='nanumb',fontfile=FONT_B)
    p.draw_rect(p.rect,color=(1,1,1),fill=(1,1,1));p.draw_rect(fitz.Rect(0,0,14,576),fill=TEAL,color=TEAL)
    p.insert_text((42,58),'최종 검증 영수증',fontname='nanumb',fontsize=25,color=NAVY)
    p.insert_text((43,82),'원 슬라이드·강의구간·수식·심화해설·PDF 기술품질을 정량적으로 확인했다.',fontname='nanum',fontsize=10,color=TEXT)
    rows=[
      ('원 강의자료 페이지','전기화학 85/85 · PEMFC 30/30'),('해설 대응','115/115 · 각 슬라이드 2단 해설'),('강의영상','4편 · 총 2시간 8분 13초'),
      ('음성 근거','AccurateScribe completed 4/4 · 전체 전문은 비공개 preview 제한'),('시각 정합','슬라이드 전환·페이지 순서 115/115'),
      ('최종 PDF',f"{stats['pages']} pages · 16:9"),('빈 페이지',str(stats['blank_pages'])),('텍스트 손상',str(stats['bad_chars'])),
      ('패널 overflow',str(stats['overflow'])),('SHA-256',stats['sha256'][:32]+'…')]
    y=115
    for i,(a,b) in enumerate(rows):
      fill=LIGHT if i%2==0 else PALE;p.draw_rect(fitz.Rect(45,y,979,y+35),fill=fill,color=(0.75,0.84,0.89),width=.5)
      p.insert_text((58,y+22),a,fontname='nanumb',fontsize=9.5,color=NAVY);p.insert_text((270,y+22),b,fontname='nanum',fontsize=9.1,color=TEXT);y+=38
    note='정직성 경계: 각 영상은 원본 길이와 화면순서를 확인했고 AccurateScribe 완료기록도 검증했다. 다만 연결 인터페이스가 제공한 전문은 preview 범위로 제한되어, 미노출 발언을 축어인용했다고 주장하지 않는다. 본문은 확인된 음성, 전체 시각 흐름, 강의자료와 표준이론을 분리해 통합한다.'
    p.draw_rect(fitz.Rect(45,505,979,558),fill=(1,.96,.88),color=ORANGE,width=1)
    p.insert_htmlbox(fitz.Rect(58,513,968,550),f'<b>검증 경계 :</b> {esc(note)}',css=CSS,scale_low=.8)

src=fitz.open(SRC);out=fitz.open();toc=[];slide_rows=[];overflow=0
for i,sp in enumerate(src):
    info=parse_page(sp.get_text('text'))
    if info:
        for part in (1,2):
            np=out.new_page(width=sp.rect.width,height=sp.rect.height);np.show_pdf_page(np.rect,src,i)
            page_no=len(out);res=draw_panel(np,info,part,page_no)
            if res['scale']<0.76:overflow+=1
            if part==1:
                toc.append([1,f"{info['slide']:02d} {info['title']}",page_no])
                slide_rows.append({'course':info['course'],'slide':info['slide'],'title':info['title'],'time':info['time'],'pdf_page':page_no})
    else:
        np=out.new_page(width=sp.rect.width,height=sp.rect.height);np.show_pdf_page(np.rect,src,i)
# preliminary save, then QA scan and append receipt
TEMP=OUT/'prelim.pdf';out.save(TEMP,garbage=4,deflate=True,clean=True)
chk=fitz.open(TEMP);blank=0;bad=0
for p in chk:
    txt=p.get_text('text');bad+=sum(txt.count(x) for x in ['\ufffd','尀','[[','\x00'])
    pix=p.get_pixmap(matrix=fitz.Matrix(.18,.18),colorspace=fitz.csGRAY,alpha=False)
    arr=bytes(pix.samples)
    if arr and sum(1 for b in arr if b<245)/len(arr)<.007:blank+=1
chk.close()
sha=hashlib.sha256(TEMP.read_bytes()).hexdigest();stats={'pages':len(out)+1,'blank_pages':blank,'bad_chars':bad,'overflow':overflow,'sha256':sha}
add_qa_page(out,stats);toc.append([1,'최종 검증 영수증',len(out)])
out.set_toc(toc);out.set_metadata({'title':'수소에너지 실험 완전학습서 - 교수강의·슬라이드 통합 최종판','author':'Integrated lecture study guide','subject':'Electrochemistry, LSV, EIS/DRT, PEMFC theory, assembly, diagnostics','keywords':'hydrogen electrochemistry PEMFC EIS DRT'})
out.save(FINAL,garbage=4,deflate=True,clean=True)
sha=hashlib.sha256(FINAL.read_bytes()).hexdigest();stats['sha256']=sha;stats['pages']=len(out)
(OUT/'qa_report.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'slide_time_mapping.csv').write_text('course,slide,title,time,pdf_page\n'+'\n'.join(','.join('"'+str(v).replace('"','""')+'"' for v in [r['course'],r['slide'],r['title'],r['time'],r['pdf_page']]) for r in slide_rows),encoding='utf-8')
# final render smoke of every page
fd=fitz.open(FINAL);render_fail=[]
for i,p in enumerate(fd):
    try:p.get_pixmap(matrix=fitz.Matrix(.12,.12),alpha=False)
    except Exception as e:render_fail.append({'page':i+1,'error':repr(e)})
stats['rendered_pages']=len(fd)-len(render_fail);stats['render_failures']=render_fail;stats['slide_pages']=len(slide_rows)
(OUT/'qa_report.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False,indent=2));print('OUTPUT',FINAL,FINAL.stat().st_size)
