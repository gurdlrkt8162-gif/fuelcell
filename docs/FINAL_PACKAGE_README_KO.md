# P1–P5 검증 코어 RAW 데이터 통합 패키지

이 문서는 P1–P5 연구를 실제 수치 데이터로 구체화하기 위해 구축한 단일 GitHub Actions artifact의 내용·범위·검증 경계를 설명한다.

## 패키지 목적

- 공개 저장소에서 실제 수치 파일을 내려받아 한 ZIP artifact로 제공
- 원 출처·버전·파일명·체크섬·다운로드 로그 보존
- ZIP CRC, 파일 크기, SHA-256 및 HTML 오류 페이지 위장 여부 검증
- MATLAB/Simulink/Simscape에서 읽을 수 있는 원본 파일과 메타데이터 동봉
- 측정값, 가공자료, 모델 파생값을 구분

## 디렉터리

- `01_PEMFC/`: FC01, FC02, FC04, FC05, FC11, FC16, FC17 및 FC06
- `02_BATTERY/`: NASA aging, CALCE A123 LFP OCV·동적 프로파일, CALCE cycling, battery EIS·raw 자료
- `03_MISSION/`: CMU UAV 실제 비행 기록, AERO4River USV 3-DoF 자료
- `04_BOP/`: MetroPT-3 압축기 및 공개 BoP/PHM 자료
- `05_SUPERCAP/`: 100 F EDLC 40°C ESR·용량·EIS
- `99_AUDIT/`: 전체 manifest, SHA-256, ZIP CRC 검사, 중복 검출, 실행 로그, 원 다운로드 스크립트

## 논문별 사용

### P1
PEMFC 분극·공간분해 전류밀도·EIS·장기 열화의 상태특징과 운전조건 민감도 분석. 같은 스택·같은 시험 캠페인을 독립 외부검증으로 오인하지 않는다.

### P2
LFP OCV/동적 등가회로, USV 운동모델, PEMFC purge 동특성의 하위모델 보정. 서로 다른 실험체의 데이터를 동일 USV 통합 실측으로 표현하지 않는다.

### P3
실제 UAV 임무부하, battery SOH, supercapacitor ESR/C/EIS의 모델링. 5 Hz급 임무 기록을 kHz 전력전자 과도응답의 실측값으로 확대하지 않는다.

### P4A/P4B
정상·열화·purge·운전조건 변화의 진단 feature 개발과 외부검증. 수동 데이터만으로 능동 진단의 인과효과를 주장하지 않는다.

### P5
stack capability, battery aging, compressor/BoP PHM 방법 검증. 일반 압축기 고장을 목표 PEMFC BoP의 직접 SOH/EOL label로 동일시하지 않는다.

## 필수 분석 경계

1. 저장소 레코드가 다르더라도 SHA-256/MD5가 같거나 동일 스택·시험 구간이면 동일 evidence unit으로 묶는다.
2. EIS에서 frequency 열 또는 검증된 frequency mapping이 없으면 Bode, Kramers–Kronig, DRT, time constant 식별을 수행하지 않는다.
3. `psig`와 절대압, `mA/cm²`와 `A/cm²`, `mW/cm²`와 `W/cm²`를 명시적으로 변환한다.
4. CSV row나 EIS frequency point를 무작위 분할하지 않고 cell/stack/spectrum/mission/route/test 단위 group split을 사용한다.
5. 원본은 읽기 전용으로 보존하고 전처리·특징·Simulink 입력은 별도 파생 폴더에 생성한다.
6. 다운로드 가능성과 재배포 허용은 별개다. 각 원 저장소의 license와 citation을 유지한다.

## 검증 산출물

- `99_AUDIT/FINAL_FILE_MANIFEST.csv`
- `99_AUDIT/FINAL_FILE_MANIFEST.json`
- `99_AUDIT/SHA256SUMS.txt`
- `99_AUDIT/ZIP_INTEGRITY.csv`
- `99_AUDIT/DUPLICATE_SHA256.json`
- `99_AUDIT/PACKAGE_SUMMARY.json`

## 주요 출처

- ZSW/RealHyFC Zenodo 19068126, 20715542
- DATAUBFC Zenodo 13166135
- Fuel-cell durability Zenodo 7054555, 3631156
- ECSIM `pem-dataset1` v1.1, CC BY 4.0
- NASA PCoE Battery Dataset
- CALCE A123 LFP data
- CMU KiltHub UAV dataset 12683453
- UCI MetroPT-3
- UTwente MetSuperCap Zenodo 20271680
- Mendeley Data FC06 and MIS04

패키지는 공개 데이터 기반 모델링·외부검증을 위한 코어 자료다. 목표 하이브리드 시스템의 통합 실험을 수행한 것으로 해석해서는 안 된다.
