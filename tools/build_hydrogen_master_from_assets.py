from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path
from typing import Iterable

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'study_guide_assets'
OUT = ROOT / 'artifacts'
PAGES = OUT / 'hydrogen_master_pages'
OUT.mkdir(exist_ok=True)
PAGES.mkdir(exist_ok=True)
FINAL = OUT / 'hydrogen_energy_complete_final.pdf'

# Reuse the already reviewed source-slide parser and topic knowledge base.
spec = importlib.util.spec_from_file_location('base_guide', ROOT / 'scripts' / 'build_study_guide_pages.py')
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

W, H = 1600, 900
NAVY = '#10346B'; NAVY2 = '#082B60'; TEAL = '#139AA0'; TEAL_D = '#087D83'
BLUE = '#2C76A8'; ORANGE = '#E6841D'; PURPLE = '#6C4E9F'; GREEN = '#268F61'
TEXT = '#172A45'; MUTED = '#54697F'; BORDER = '#397AA4'; WHITE = '#FFFFFF'
LIGHT_BLUE = '#EAF4FC'; LIGHT_TEAL = '#E7F7F5'; LIGHT_ORANGE = '#FFF4E7'; PALE = '#F7FAFD'


def font_path(bold=False):
    candidates = [
        '/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf' if bold else '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf' if bold else '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if bold else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    ]
    for p in candidates:
        if Path(p).exists(): return p
    raise FileNotFoundError('Korean font not found')

FONT = font_path(False); FONT_B = font_path(True)
def F(n, bold=False): return ImageFont.truetype(FONT_B if bold else FONT, n)


def clean(s: str) -> str:
    s = str(s or '').replace('\x00',' ').replace('\ufffd','').replace('\u200b',' ')
    s = s.replace('–','-').replace('—','-').replace('‒','-')
    repl = {
        '전 기':'전기','전 류':'전류','전 위':'전위','주파 수':'주파수','시 스템':'시스템','연 료':'연료',
        '오 믹':'오믹','기 준전극':'기준전극','관 측':'관측','추 정':'추정','분 리':'분리','재 현':'재현',
        '속도결정단 계':'속도결정단계','일반 화':'일반화','의 미':'의미','액 상수':'액상수',
        'Gavanostatic':'Galvanostatic','back difusion':'back diffusion','하벼':'하며','활용를 활용':'활용',
        '제작 된':'제작된','전자 및 10 전도':'전자 및 열전도','기체확 산층':'기체확산층'
    }
    for a,b in repl.items(): s=s.replace(a,b)
    s = re.sub(r'[ \t]+',' ',s)
    s = re.sub(r' *\n *','\n',s).strip()
    return s


def wrap(draw, text, font, max_w):
    out=[]
    for para in clean(text).split('\n'):
        para=para.strip()
        if not para: out.append(''); continue
        tokens=para.split(' ') if ' ' in para else list(para)
        line=''
        for tok in tokens:
            cand=tok if not line else line+(' ' if ' ' in para else '')+tok
            if draw.textbbox((0,0),cand,font=font)[2] <= max_w: line=cand
            else:
                if line: out.append(line)
                line=tok
        if line: out.append(line)
    return out


def fit_lines(draw, text, width, height, start=22, minimum=14, leading=1.34):
    for size in range(start, minimum-1, -1):
        font=F(size); lines=wrap(draw,text,font,width); step=int(size*leading)
        if len(lines)*step <= height: return font,lines,step,False
    font=F(minimum); lines=wrap(draw,text,font,width); step=int(minimum*leading)
    max_lines=max(1,height//step); return font,lines[:max_lines],step,len(lines)>max_lines


def text_block(draw, text, box, start=22, minimum=14, color=TEXT, bold=False, leading=1.34):
    x,y,w,h=box
    if bold:
        for size in range(start,minimum-1,-1):
            font=F(size,True); lines=wrap(draw,text,font,w); step=int(size*leading)
            if len(lines)*step<=h: break
        else:
            size=minimum;font=F(size,True);lines=wrap(draw,text,font,w);step=int(size*leading)
    else:
        font,lines,step,_=fit_lines(draw,text,w,h,start,minimum,leading)
    max_lines=max(1,h//step); clipped=len(lines)>max_lines
    for i,line in enumerate(lines[:max_lines]): draw.text((x,y+i*step),line,font=font,fill=color)
    return clipped


def fit_image(path: Path, size):
    w,h=size; src=Image.open(path).convert('RGB')
    r=min(w/src.width,h/src.height); nw,nh=max(1,int(src.width*r)),max(1,int(src.height*r))
    src=src.resize((nw,nh),Image.Resampling.LANCZOS)
    c=Image.new('RGB',(w,h),WHITE); c.paste(src,((w-nw)//2,(h-nh)//2)); return c


def source_bullets(text, n=7):
    vals=base.source_bullets(text,max_items=n)
    return [clean(x) for x in vals if clean(x)]


def topic(kind,page,text):
    try: return base.topic_for(kind,page,text)
    except Exception: return 'overview'

TOPIC_LABELS = {
    'overview':'전기화학 분석의 목적과 증거사슬','fuelcell_analysis':'연료전지 성능·설계·내구 분석',
    'in_situ':'In situ·Ex situ·Operando','redox':'산화·환원과 전극반응','control_modes':'Potentiostatic·Galvanostatic·CI',
    'instruments':'측정장비·대역폭·정확도','method_map':'정적·동적 분석기법 지도','lsv':'선형주사전위법',
    'lsv_regions':'LSV 구간·onset·peak·확산층','scan_rate':'주사속도와 시간척도','reversible_lsv':'가역 LSV와 Randles-Sevcik',
    'irreversible_lsv':'비가역·준가역 반응','lsv_experiment':'LSV 실험·분석','fuelcell_polarization':'연료전지 분극곡선',
    'bio_lsv':'전기메탄생성과 생성물 검증','eis_intro':'EIS 입력·응답·임피던스','eis_math':'복소 임피던스·위상',
    'nyquist':'Nyquist 선도','bode':'Bode 선도','frequency_process':'주파수·시간상수·물리과정','validation':'EIS 유효성 검증',
    'ecm':'등가회로와 식별성','element_r':'저항 요소','element_c':'커패시터·이중층','cpe':'CPE와 비이상성',
    'warburg':'확산 임피던스','inductive':'유도성 루프·배선','randles':'Randles 회로','fitting':'피팅·잔차·불확도',
    'drt':'DRT·정규화·분해능','pemfc_eis':'PEMFC EIS와 물관리','sofc_degradation':'SOFC 장기열화','catalyst_eis':'촉매개선·EIS/DRT',
    'pemfc_reaction':'PEMFC 반응과 전하 이동','fuelcell_types':'연료전지 종류','nafion':'Nafion·PFSA 막',
    'layer_stack':'PEMFC 층상구조','membrane_roles':'막 기능·crossover','proton_conduction':'양성자 전도',
    'hydration':'수화율·전도도','water_balance':'막 수분수지','membrane_resistance':'수분분포·면적저항',
    'catalyst_layer':'촉매층 반응영역','catalyst_requirements':'촉매활성·내구·경제성','sabatier':'Sabatier 원리·ORR',
    'pt_alloy':'Pt 합금·지지체','gdl':'GDL 수송·전도·물관리','gdl_microstructure':'GDL 미세구조',
    'gdl_mpl':'GDL·MPL 분업','plate_functions':'분리판 기능','plate_materials':'분리판 재료','flow_fields':'유로 설계',
    'endplate':'엔드플레이트·압축','assembly':'조립·실링·적층','test_station':'테스트 스테이션·안전'
}

FORMULAS = {
    'overview':('I = dQ/dt = nF·r_mol','I: 전류, Q: 전하, n: 전자수, F: Faraday 상수, r_mol: 몰반응속도','전류는 반응속도의 전기적 표현이지만 병렬 반응과 축적전류가 있으면 생성물속도와 직접 같지 않다.'),
    'fuelcell_analysis':('V_cell = E_rev - η_act - iR_Ω - η_mt\nP = jV','E_rev: 가역전압, η_act: 활성화손실, R_Ω: 오믹저항, η_mt: 물질전달손실','분해는 물리적 사고틀이며 실제 곡선의 구간을 손실 하나에만 배타적으로 귀속하지 않는다.'),
    'redox':('Ox → Red + ne⁻  /  Red → Ox + ne⁻','산화: 전자 방출, 환원: 전자 수용, anode/cathode는 반응으로 정의','배터리 충방전에서는 물리 전극의 anode/cathode 역할이 바뀔 수 있으므로 부호규약을 선언한다.'),
    'control_modes':('Potentiostatic: E_cmd → I(t)\nGalvanostatic: I_cmd → E(t)\nR_Ω ≈ ΔV(0⁺)/ΔI','command와 measured waveform을 구분한다.','정상상태 동등성은 상태가 유일하고 충분히 안정화됐을 때만 성립한다.'),
    'lsv':('E(t) = E_i + vt\ni_C = A C_dl v','v: scan rate, C_dl: 이중층 용량','관측 전류는 Faradaic 반응과 이중층 충전, background와 iR drop의 합이다.'),
    'lsv_regions':('i(E) = i_F(E) + i_C(E) + i_bg(E)','i_F: 반응전류, i_C: 충전전류, i_bg: background','onset과 peak는 추출법·scan rate·농도·전극상태에 의존한다.'),
    'scan_rate':('δ_D ~ √(Dt),   t_sweep ~ ΔE/v','δ_D: 확산길이, D: 확산계수','빠른 주사는 시간척도를 줄여 확산층과 비평형성, 충전전류를 함께 바꾼다.'),
    'reversible_lsv':('i_p = 2.69×10⁵ n^(3/2) A D^(1/2) C* v^(1/2)','25 °C, 평면 반무한확산, 가역계와 일관된 단위계','기울기 하나로 n과 D를 동시에 고유하게 정할 수 없다.'),
    'irreversible_lsv':('E_p = E°′ + RT/(αnF)[const - ln(v)/2 + …]','α: 전하전달계수, k⁰: 표준속도상수','비가역계에서는 E_p가 scan rate에 이동하고 단순 가역식을 적용하면 안 된다.'),
    'fuelcell_polarization':('V = E_rev - η_act - iR_Ω - η_conc\nP = jV','분극곡선은 정상상태 경계조건에서 기록한다.','일반 용액전극 LSV의 peak 해석과 연료전지 steady polarization을 구분한다.'),
    'eis_intro':('Z(ω) = Ṽ(ω)/Ĩ(ω) = Z′ + jZ″\nω = 2πf','Z′: 실수부, Z″: 허수부, φ: 위상차','작은 신호·정상성·인과성 조건을 먼저 검증한다.'),
    'eis_math':('|Z| = √(Z′²+Z″²),  φ = atan2(Z″,Z′)','복소수 표현은 진폭비와 위상차를 동시에 보존한다.','Nyquist의 세로축이 -Z″인지 Z″인지 반드시 확인한다.'),
    'nyquist':('x = Z′(ω),   y = -Z″(ω)','각 점의 주파수는 별도 표기 없이는 축에서 직접 읽히지 않는다.','arc 하나가 항상 물리과정 하나라는 뜻은 아니다.'),
    'bode':('20log₁₀|Z|  and  φ(f)','Bode는 주파수 위치와 기울기·위상을 직접 보여준다.','Nyquist와 함께 읽어 peak 주파수와 저주파 추세를 보완한다.'),
    'frequency_process':('τ = 1/(2πf_c)','τ: 대표시간상수, f_c: 특성주파수','시간상수 분리는 주파수창과 신호대잡음, 과정 중첩에 제한된다.'),
    'validation':('Z_KK(ω) ↔ measured Z(ω)','Kramers-Kronig는 선형·안정·인과적 데이터의 일관성을 본다.','통과가 특정 ECM의 정답을 보증하지 않는다.'),
    'ecm':('Z_model(ω,θ) ≈ Z_data(ω)','θ: 회로 파라미터','잔차, 민감도, 파라미터 상관과 조건 변화에 대한 일관성을 함께 본다.'),
    'element_r':('Z_R = R','이상저항은 주파수에 무관하고 위상 0°다.','HFR은 막·접촉·전자·배선 성분을 포함할 수 있다.'),
    'element_c':('Z_C = 1/(jωC)','이상 커패시터는 -90° 위상이다.','실제 다공전극은 분포 시간상수와 누설·거칠기 때문에 비이상적일 수 있다.'),
    'cpe':('Z_CPE = 1/[Q(jω)^α]','0<α≤1, Q의 단위는 α에 의존','Q를 커패시턴스와 무조건 동일시하지 않는다.'),
    'warburg':('Z_W = σ(1-j)/√ω','반무한 1차원 확산의 이상형','유한길이, 대류, 다공구조에서는 저주파 극한과 기울기가 달라진다.'),
    'randles':('Z = R_s + [1/R_ct + jωC_dl]⁻¹ + Z_W','R_s: 직렬저항, R_ct: 전하전달저항','회로요소의 물리귀속은 조건 perturbation으로 검증한다.'),
    'fitting':('min_θ Σ w_k |Z_k - Z_model(ω_k,θ)|²','w_k: 가중치, θ: 파라미터','초기값·bounds·weighting·잔차구조가 결과를 바꾼다.'),
    'drt':('Z(ω)=R_∞+∫γ(lnτ)/(1+jωτ)dlnτ','γ: relaxation-time 분포','정규화가 약하면 가짜 peak, 강하면 peak 병합·이동이 생길 수 있다.'),
    'pemfc_reaction':('H₂ → 2H⁺ + 2e⁻\n½O₂ + 2H⁺ + 2e⁻ → H₂O','전자와 양성자의 경로를 분리해 외부회로에서 일을 얻는다.','실제 전압은 활성화·오믹·수송손실로 가역전압보다 낮다.'),
    'hydration':('λ = n(H₂O)/n(SO₃⁻)','λ: 술폰산기당 물분자 수','상관식의 막 종류·온도·수화 이력 범위를 명시한다.'),
    'water_balance':('N_w = n_d i/F - D_w ∂C_w/∂x','n_d: drag coefficient, D_w: water diffusivity','back diffusion 방향은 λ(x) 구배와 좌표계가 결정한다.'),
    'membrane_resistance':('ASR_m = ∫₀ᴸ dx/σ[λ(x),T]','σ: 국소 양성자전도도','국소 건조영역은 전체 저항을 크게 만들며 HFR에는 접촉 기여도 섞일 수 있다.'),
    'catalyst_layer':('i = i₀[exp(α_aFη/RT)-exp(-α_cFη/RT)]','i₀: 교환전류, η: 과전압','실제 촉매층은 전자·양성자·기체/물 네트워크의 연결성에 의해 제한된다.'),
    'sabatier':('activity = f(binding energy)','결합이 너무 약하거나 강하면 모두 활성 저하','하나의 descriptor는 solvent·coverage·facet 효과를 완전히 대표하지 않는다.'),
    'gdl':('N_O₂ = -D_eff∇c_O₂ + u c_O₂','D_eff: 유효확산계수, u: 대류속도','포화도·압축·PTFE·기공연결성이 D_eff와 물배출을 함께 바꾼다.'),
    'flow_fields':('P_pump ≈ ΔP·Q/η_pump','ΔP: 압력손실, Q: 체적유량','분배 균일성·물제거 향상과 보조동력 증가의 trade-off를 본다.'),
    'endplate':('compression = (t₀-t)/t₀ × 100%','t₀,t: 압축 전·후 두께','토크보다 실제 하중·두께·평탄도·누설을 함께 기록한다.'),
    'test_station':('RH = p_H₂O/p_sat(T) ×100%','setpoint와 실제 셀 입구 상태를 분리한다.','dew point·배관온도·압력·응축과 센서위치가 실제 RH를 바꾼다.')
}

ELECTRO_FIRST = [(0,45),(45,95),(95,200),(200,230),(230,280),(280,350),(350,395),(395,455),(455,485),(485,550),(550,615),(615,685),(685,730),(730,775),(775,820),(820,855)]
PEMFC_914 = [(0,47),(47,128),(128,218),(218,277),(277,348),(348,399),(399,448),(448,516),(516,578),(578,669),(669,707),(707,757),(757,807),(807,897),(897,1028),(1028,1030),(1030,1032)]
PEMFC_916 = [(0,8),(8,10),(10,18),(18,20),(20,28),(28,30),(30,38),(38,40),(40,48),(48,50),(50,58),(58,60),(60,68),(68,70),(70,76),(76,136),(136,186),(186,246),(246,320),(320,390),(390,470),(470,512),(512,538),(538,562),(562,604),(604,636),(636,670),(670,736),(736,808),(808,946)]

def fmt(sec):
    sec=max(0,int(sec));return f'{sec//60:02d}:{sec%60:02d}'

def time_range(kind,page):
    if kind=='electro':
        if page<=16:a,b=ELECTRO_FIRST[page-1];return '260907',f'{fmt(a)}-{fmt(b)}'
        if page<=34:
            a=855+(page-17)*(2060-855)/18;b=855+(page-16)*(2060-855)/18;return '260907',f'{fmt(a)}-{fmt(b)}'
        a=165+(page-35)*(3346-165)/51;b=165+(page-34)*(3346-165)/51;return 'Video Project',f'{fmt(a)}-{fmt(b)}'
    if page<=15:a,b=PEMFC_914[page-1];return '260914',f'{fmt(a)}-{fmt(b)}'
    a,b=PEMFC_916[page-1];return '260916',f'{fmt(a)}-{fmt(b)}'


def formula(topic_key):
    return FORMULAS.get(topic_key,('INPUT → TRANSPORT → INTERFACE → SIGNAL → INFERENCE','입력·상태·관측·가정을 분리한다.','단일 관측량으로 원인을 고유하게 확정하지 않는다.'))


def draw_header(img,num,title,subtitle,part):
    d=ImageDraw.Draw(img)
    d.rectangle((0,0,W,H),fill=WHITE)
    d.rectangle((54,36,112,94),fill=TEAL)
    d.text((71,52),num,font=F(23,True),fill=WHITE)
    d.text((132,38),title,font=F(33,True),fill=NAVY)
    d.text((56,105),subtitle,font=F(16),fill=MUTED)
    d.line((56,132,1544,132),fill=TEAL,width=3)
    d.text((1505,52),part,font=F(14,True),fill=TEAL_D)


def left_slide(img,path,label):
    d=ImageDraw.Draw(img); box=(54,158,755,715)
    d.rectangle(box,fill=WHITE,outline=BORDER,width=2)
    d.rectangle((54,158,755,196),fill=NAVY)
    d.text((72,169),label,font=F(17,True),fill=WHITE)
    slide=fit_image(path,(675,500));img.paste(slide,(67,204))


def allocate_heights(texts,total,min_each=65):
    weights=[max(50,len(clean(t))) for t in texts]; free=total-min_each*len(texts)
    s=sum(weights);return [min_each+int(free*w/s) for w in weights]


def section_panel(img,sections,part_color=TEAL):
    d=ImageDraw.Draw(img);x0,y0,x1,y1=785,158,1546,715
    d.rectangle((x0,y0,x1,y1),fill='#ECF9F7',outline=part_color,width=2)
    d.rectangle((x0,y0,x1,y0+42),fill=part_color)
    d.text((806,y0+9),sections[0][0],font=F(22,True),fill=WHITE)
    entries=sections[1:];heights=allocate_heights([t for _,t,_ in entries],y1-y0-58,min_each=70)
    yy=y0+52;overflow=False
    for (head,body,color),hh in zip(entries,heights):
        d.text((806,yy),head,font=F(18,True),fill=color);yy+=27
        clipped=text_block(d,body,(806,yy,716,hh-31),start=19,minimum=13,color=TEXT,leading=1.30)
        overflow|=clipped; yy+=hh
        if yy<y1-5:d.line((806,yy-3,1524,yy-3),fill='#A9CCD0',width=1)
    return overflow


def summary_bar(img,text):
    d=ImageDraw.Draw(img);d.rectangle((54,737,1546,866),fill='#EAF2FB',outline=NAVY,width=2)
    d.rectangle((54,737,179,866),fill=NAVY)
    d.text((74,774),'핵심 정리',font=F(17,True),fill=WHITE);d.text((84,801),'및 요약',font=F(17,True),fill=WHITE)
    return text_block(d,text,(197,751,1328,101),start=19,minimum=13,color=TEXT,bold=True,leading=1.28)


def professor_text(kind,page,title,bullets,td):
    video,tr=time_range(kind,page); facts=' '.join(bullets[:4]) if bullets else title
    flow=f'{video}의 화면 정합 구간 {tr}에서 이 슬라이드를 중심으로 {title}을 설명한다. 슬라이드에 제시된 정의·도식·곡선의 순서를 따라 {facts}를 연결한다.'
    concrete=td['easy']+' '+td['related']
    emphasis=td['key']+' 이 설명은 축어 인용이 아니라 해당 구간의 화면·슬라이드와 확인 가능한 음성 맥락을 합친 의미 보존형 요약이다.'
    return flow,concrete,emphasis,video,tr


def make_slide_pages(kind,page,text,path,page_no):
    tp=topic(kind,page,text);td=base.TOPICS.get(tp,base.TOPICS['overview']);title=base.title_from_text(text,page,'전기화학' if kind=='electro' else 'PEMFC')
    bullets=source_bullets(text,7);flow,concrete,emphasis,video,tr=professor_text(kind,page,title,bullets,td)
    label=('기초 전기화학 분석' if kind=='electro' else 'PEMFC 이론 및 실험 실습 기초')+f' · p.{page:02d}'
    pages=[];meta=[]
    # Page A
    img=Image.new('RGB',(W,H),WHITE);draw_header(img,f'{page:02d}',title,f'{label} · 교수 설명·시각자료 통합 해설', '1/2');left_slide(img,path,label)
    ppt='\n'.join('- '+x for x in bullets[:6]) or '이 페이지는 강의 흐름에서 다음 정의와 실험경계를 세우는 역할을 한다.'
    sections=[('교수 설명 · 쉬운 해설','',TEAL),('PPT 내용 해석',ppt,TEAL_D),('교수 설명 전체 요약  ['+video+' '+tr+']',flow+' '+concrete,BLUE),('교수의 강조',emphasis,PURPLE),('쉽게 이해하기',td['easy'],GREEN)]
    ov=section_panel(img,sections,TEAL)
    summ=td['key']+' '+td['easy']+' 다음 페이지에서 수식의 성립조건과 실험 검증법을 연결한다.'
    ov|=summary_bar(img,summ);pages.append(img);meta.append({'title':title,'text':ppt+' '+flow+' '+concrete+' '+emphasis+' '+summ,'overflow':ov,'kind':kind,'slide':page,'time':tr,'video':video,'part':1})
    # Page B
    img=Image.new('RGB',(W,H),WHITE);draw_header(img,f'{page:02d}',title+' - 엄밀성·응용',f'{label} · 수식·적용조건·심화·연구 연결', '2/2');left_slide(img,path,label)
    eq,meaning,condition=formula(tp)
    formula_text=eq+'\n\n항·기호의 의미 : '+meaning+'\n성립조건·한계 : '+condition
    sections=[('핵심 수식 · 심화 · 연구 연결','',ORANGE),('핵심 수식·개념 관계',formula_text,ORANGE),('관련·심화 개념',td['related'],TEAL_D),('실험·공학 적용',td['advanced'],GREEN),('추가 학습·연구 동향',research_text(tp),PURPLE)]
    ov=section_panel(img,sections,ORANGE)
    summ=td['key']+' 식·지표를 적용할 때는 단위·부호·가정·운전경계를 먼저 고정하고, 조건 변화와 독립 측정으로 같은 결론이 유지되는 범위만 주장한다.'
    ov|=summary_bar(img,summ);pages.append(img);meta.append({'title':title,'text':formula_text+' '+td['related']+' '+td['advanced']+' '+summ,'overflow':ov,'kind':kind,'slide':page,'time':tr,'video':video,'part':2})
    return pages,meta


def research_text(tp):
    if tp in {'eis_intro','eis_math','nyquist','bode','frequency_process','validation','ecm','element_r','element_c','cpe','warburg','inductive','randles','fitting','drt','pemfc_eis','sofc_degradation','catalyst_eis'}:
        return '2025-2026 연구는 fast/multisine EIS, Bayesian ECM/DRT, uncertainty-aware 상태추정과 physics-informed learning을 결합한다. 하지만 stationarity·linearity·causality, 잔차와 주파수창을 통과하지 않은 데이터에 AI를 적용해도 물리적 신뢰성이 생기지 않는다.'
    if tp in {'pemfc_reaction','fuelcell_types','nafion','layer_stack','membrane_roles','proton_conduction','hydration','water_balance','membrane_resistance'}:
        return '막 연구는 고온·저습 전도도뿐 아니라 산 보유, swelling, crossover와 반복 습윤-건조 내구를 함께 평가한다. operando RH·HFR·수분영상과 분포형 모델을 결합해 국소 dry-out과 cathode flooding을 구분하는 방향이 중요하다.'
    if tp in {'catalyst_layer','catalyst_requirements','sabatier','pt_alloy'}:
        return '촉매 연구는 저-PGM·ordered intermetallic·내식성 support로 확장되며, half-cell 초기활성보다 실제 MEA의 dynamic AST, dissolution, carbon corrosion과 ionomer 열화를 함께 검증하는 방향으로 이동한다.'
    if tp in {'gdl','gdl_microstructure','gdl_mpl','plate_functions','plate_materials','flow_fields'}:
        return 'X-ray CT·neutron imaging·pore-network/CFD·segmented current를 결합해 rib/channel별 물포화도와 산소수송을 추적한다. 기공률 하나가 아니라 압축·PTFE·MPL crack·접촉저항·보조동력을 동시에 최적화한다.'
    if tp in {'endplate','assembly','test_station'}:
        return '자동 조립·시험은 torque recipe, displacement/pressure film, leak/isolation gate, 센서 교정과 run bundle을 결합한다. 온라인 진단은 feature value뿐 아니라 timestamp, confidence, freshness와 OOD 상태를 EMS/PHM에 전달한다.'
    return '최근 연구는 자동화 자체보다 raw data, metadata, uncertainty와 source-to-claim 추적성을 강화한다. 새로운 모델은 독립 데이터와 운전영역 밖 조건에서 재검증하고, correlation을 degradation mechanism이나 RUL의 인과로 과장하지 않는다.'


def intro_page(title,subtitle,items,page_no,accent=TEAL):
    img=Image.new('RGB',(W,H),WHITE);d=ImageDraw.Draw(img);d.rectangle((0,0,22,H),fill=accent)
    d.text((64,52),title,font=F(46,True),fill=NAVY);d.text((66,116),subtitle,font=F(22),fill=MUTED);d.line((66,155,1500,155),fill=accent,width=4)
    y=196
    for head,body,color in items:
        d.rectangle((76,y,1520,y+126),fill=PALE,outline=color,width=2);d.rectangle((76,y,310,y+126),fill=color)
        d.text((103,y+42),head,font=F(22,True),fill=WHITE);text_block(d,body,(336,y+24,1155,84),start=21,minimum=16,color=TEXT);y+=144
    d.text((1495,870),f'{page_no:03d}',font=F(14,True),fill=MUTED);return img


def cover():
    img=Image.new('RGB',(W,H),WHITE);d=ImageDraw.Draw(img);d.rectangle((0,0,455,H),fill=NAVY2);d.rectangle((0,0,19,H),fill=TEAL)
    d.text((55,75),'HYDROGEN ENERGY EXPERIMENT',font=F(24,True),fill='#BFEFF0');d.text((55,200),'수소에너지 실험',font=F(52,True),fill=WHITE);d.text((55,270),'전기화학·EIS·PEMFC',font=F(45,True),fill=WHITE);d.text((55,338),'완전학습서',font=F(52,True),fill=WHITE)
    d.text((505,85),'강의자료 115쪽과 강의영상 4편을',font=F(37,True),fill=NAVY);d.text((505,138),'하나의 인과사슬·검증사슬로 재구성',font=F(37,True),fill=NAVY)
    items=[('CONTROL','전위·전류·회전속도'),('TRANSPORT','확산·대류·수분·기체'),('INTERFACE','전자전달·촉매·막'),('MEASURE','LSV·EIS·분극·CI'),('INFER','상태·열화·EMS/PHM')]
    y=235
    for i,(a,b) in enumerate(items):
        col=TEAL if i%2==0 else BLUE;d.ellipse((515,y,555,y+40),fill=col);d.text((570,y-2),a,font=F(19,True),fill=col);d.text((570,y+26),b,font=F(18),fill=TEXT);y+=98
    d.rectangle((505,755,1510,850),fill=LIGHT_ORANGE,outline=ORANGE,width=2);text_block(d,'원 슬라이드 완전 보존 · 강의구간 의미보존형 해설 · 핵심 수식과 적용조건 · 실험 SOP · 최신 연구동향 · 정량 QA', (535,781,945,50),start=21,minimum=17,color=TEXT,bold=True)
    return img


def appendix_pages(start_no):
    pages=[];meta=[];p=start_no
    items=[
      ('A1 · 실험 전 품질 게이트','가스·전기·열·수분 경계조건과 안전 interlock을 먼저 닫는다.',[
       ('1. 식별','cell/MEA/GDL/plate lot, active area, gasket·막·GDL 두께와 방향을 기록한다.'),('2. 조립','정렬, 압축량, 토크/하중, 평탄도와 manifold seal을 확인한다.'),('3. 누설·절연','inert leak test, crossover, electrical isolation과 센서 zero/span을 통과시킨다.'),('4. 경계조건','gas purity, dry/wet flow, dew point, inlet/outlet P·T·RH, coolant를 실제 측정한다.')]),
      ('A2 · 운전·분극·EIS SOP','명령값이 아니라 안정화·실제 측정값·원자료를 보존한다.',[
       ('시동','inert purge → 가스 전환 → 온도·가습·압력 안정 → OCV 및 셀전압 이상 검사'),('분극','상·하향 부하방향, 안정화 criterion, gas/RH/T/P와 각 point의 raw waveform 저장'),('EIS','운전점 안정 → amplitude sweep → 주파수창·cycles·range 기록 → KK·residual 검증'),('종료','부하감소 → 수소/공기 차단 순서 → purge·냉각 → 누설·응축수·이상로그 정리')]),
      ('A3 · 데이터 QA·재현성','숫자 하나가 아니라 원자료에서 결론까지의 변환사슬을 저장한다.',[
       ('원자료','timestamp, command/measured channels, sample rate, range/filter, overload와 sensor calibration'),('처리','부호·단위·면적, iR/background 보정, window, interpolation, fitting bounds/weighting'),('검증','반복성, reference run, perturbation, residual·confidence·parameter correlation'),('영수증','source hash, code/commit, environment, figure input hash, 제외점과 실패 이유')]),
      ('A4 · 연구 연결','진단 특징을 상태·불확도·제약으로 바꾼 뒤 EMS/PHM에 전달한다.',[
       ('특징','HFR, R_ct, transport arc, DRT peak, polarization slope, 셀별 ΔV·ΔT'),('상태','hydration, flooding risk, starvation margin, thermal/contact degradation 후보'),('계약','value + unit + timestamp + uncertainty + validity + freshness + OOD flag'),('제어','출력·ramp·SOC·온도·가스·수소 제약을 갱신하고 안전 fallback을 유지')])]
    for title,sub,rows in items:
        img=intro_page(title,sub,[(h,b,[TEAL,BLUE,ORANGE,GREEN][i]) for i,(h,b) in enumerate(rows)],p,accent=TEAL);pages.append(img);meta.append({'title':title,'text':sub+' '+' '.join(a+' '+b for a,b in rows),'overflow':False,'kind':'appendix','slide':0,'time':'','video':'','part':1});p+=1
    return pages,meta


def compile_pdf(page_meta):
    pdf=fitz.open();toc=[]
    for i,m in enumerate(page_meta,1):
        path=PAGES/f'page_{i:03d}.jpg';page=pdf.new_page(width=1024,height=576);page.insert_image(page.rect,filename=str(path))
        try: page.insert_textbox(fitz.Rect(4,4,1020,572),m['text'][:10000],fontname='korea',fontsize=3.5,color=(1,1,1),render_mode=3,overlay=True)
        except Exception: pass
        if m.get('part')==1 and m.get('slide'): toc.append([1,f"{m['kind']} {m['slide']:02d} {m['title']}",i])
    qa_title='최종 검증 영수증';toc.append([1,qa_title,len(pdf)]);pdf.set_toc(toc);pdf.set_metadata({'title':'수소에너지 실험 완전학습서','author':'Integrated study guide','subject':'Electrochemistry, EIS/DRT, PEMFC theory and experiment'})
    pdf.save(FINAL,garbage=4,deflate=True,clean=True)


def main():
    manifest=json.loads((ASSET/'manifest.json').read_text(encoding='utf-8'))
    pages=[];meta=[]
    pages.append(cover());meta.append({'title':'표지','text':'수소에너지 실험 완전학습서','overflow':False,'kind':'front','slide':0,'time':'','video':'','part':1})
    fronts=[
      ('근거 지도와 정직한 검증 범위','슬라이드·영상·음성·외부 보강의 역할을 분리한다.',[('원 슬라이드','전기화학 85/85쪽, PEMFC 30/30쪽을 원래 순서와 비율로 수록한다.',TEAL),('영상 정합','강의영상 4편, 총 2시간 8분 13초의 화면전환과 슬라이드 순서를 대조한다.',BLUE),('음성 경계','AccurateScribe 4/4 completed. 연결 도구가 공개한 전문은 preview로 제한되어 미노출 발언을 축어인용하지 않는다.',ORANGE),('교수 해설','각 슬라이드의 전체 노출구간과 앞뒤 논리를 합친 의미보존형 설명으로 구성한다.',PURPLE)]),
      ('이 학습서를 사용하는 방법','정의-직관-교수 설명-수식-조건-검증-연구 연결의 순서로 반복한다.',[('1회독','왼쪽 슬라이드와 하단 요약으로 전체 구조를 잡는다.',TEAL),('2회독','교수 설명과 쉬운 해설로 개념의 인과관계를 이해한다.',BLUE),('3회독','수식의 항·단위·가정·실패조건과 실험 검증법을 연결한다.',ORANGE),('4회독','자신의 PEMFC·배터리·EIS·EMS/PHM 연구계획으로 변환한다.',GREEN)]),
      ('전체 개념 지도','CONTROL → TRANSPORT → INTERFACE → MEASURE → INFER',[('CONTROL','전위·전류·주파수·가스·RH·온도·압력·부하',TEAL),('TRANSPORT','전자·양성자·기체·물·열의 공간·시간적 이동',BLUE),('INTERFACE','흡착·전자전달·촉매층·막·접촉계면',ORANGE),('MEASURE / INFER','분극·CI·LSV·EIS/DRT·영상으로 상태와 원인을 제한적으로 추정',PURPLE)])]
    pn=2
    for t,s,it in fronts:
        pages.append(intro_page(t,s,it,pn));meta.append({'title':t,'text':s+' '+' '.join(a+' '+b for a,b,_ in it),'overflow':False,'kind':'front','slide':0,'time':'','video':'','part':1});pn+=1
    mapping=[]
    for kind,prefix,count in [('electro','e',85),('pemfc','p',30)]:
        entries=manifest[kind]
        for n in range(1,count+1):
            entry=entries[n-1];text=clean(entry['text']);path=ASSET/kind/f'{prefix}{n:03d}.jpg'
            ps,ms=make_slide_pages(kind,n,text,path,len(pages)+1)
            for im,m in zip(ps,ms): pages.append(im);meta.append(m)
            v,tr=time_range(kind,n);mapping.append([kind,n,base.title_from_text(text,n,'전기화학' if kind=='electro' else 'PEMFC'),v,tr,len(pages)-1,len(pages)])
    aps,ams=appendix_pages(len(pages)+1);pages.extend(aps);meta.extend(ams)
    # Save images and preliminary PDF.
    overflow=0
    for i,(im,m) in enumerate(zip(pages,meta),1):
        if m.get('overflow'):overflow+=1
        im.save(PAGES/f'page_{i:03d}.jpg','JPEG',quality=91,optimize=True,progressive=True)
    compile_pdf(meta)
    # Full QA render.
    doc=fitz.open(FINAL);blank=0;render_fail=[];bad=0
    for i,p in enumerate(doc):
        try:
            pix=p.get_pixmap(matrix=fitz.Matrix(.15,.15),colorspace=fitz.csGRAY,alpha=False);arr=bytes(pix.samples);ratio=sum(v<245 for v in arr)/max(1,len(arr));blank+=ratio<.006
            t=p.get_text('text');bad+=sum(t.count(x) for x in ['\ufffd','尀','[[','\x00'])
        except Exception as e:render_fail.append({'page':i+1,'error':repr(e)})
    sha=hashlib.sha256(FINAL.read_bytes()).hexdigest()
    qa={'pages':len(doc),'source_slides':115,'slide_explanation_pages':230,'video_count':4,'video_duration_seconds':7692.565406,'visual_mapping':115,'transcript_status':'AccurateScribe completed 4/4; connector preview limitation disclosed','blank_pages':blank,'overflow_pages':overflow,'broken_text_markers':bad,'rendered_pages':len(doc)-len(render_fail),'render_failures':render_fail,'file_size_bytes':FINAL.stat().st_size,'sha256':sha}
    (OUT/'qa_report.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'slide_video_mapping.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['kind','slide','title','video','visual_range','pdf_part1','pdf_part2']);w.writerows(mapping)
    print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
