# 추가 PEMFC 공개데이터 엄격 선별 보고

이번 패키지는 기존 Google Drive 패키지를 대체하지 않고, 추가로 검증 가치가 확인된 데이터만 담습니다. 후보를 많이 모으는 것이 아니라 **물리적 관련성, 측정변수, 프로토콜, 권리, 파일 무결성, 파싱 가능성, 두 원고의 주장 경계**를 모두 통과한 자료만 승인했습니다.

## 승인 데이터

|ID|분류|핵심 가치|주요 한계|
|---|---|---|---|
|ADD01_RWTH_FULL_SCALE_MPC|CORE — system/BoP dynamic operation|F-AAV and AUV: stack voltage/current, stack power/efficiency, air/H2/coolant commands and responses, reactant pressures, membrane hydration/temperature, stoichiometry, coolant ΔT and dynamic cycle validation.|Full-scale research test bench but not the 2×250 kW F-AAV module and not an underwater AIP plant. Includes measured raw signals and calculated internal-state channels; keep authority labels separate.|
|ADD02_SEVILLA_CELL_DYNAMICS|CORE — variable-rich single-cell operating data|Both manuscripts: pressure/flow/humidity/temperature/current/voltage response, temperature and pressure sensitivity, cathode stoichiometry sensitivity, NEDC transient-load replay, cell-level model qualification.|50 cm² single cell, not system-net efficiency or module start/stop evidence. Raw files are tab-delimited text without extensions and require the supplied importer and channel dictionary.|
|ADD03_DIFFERENTIAL_LOCAL_EIS|CORE — EIS/polarization under controlled local conditions|Both manuscripts and EIS/PHM papers: 37 local conditions spanning RH, temperature, pressure and gas-composition emulation at inlet/middle/outlet; polarization and EIS at 45/180/900 mA; build physically indexed electrochemical maps.|Differential cell and emulated local conditions, not a complete stack/BoP or vehicle system. One Dataverse normalized/original representation mismatch is documented; the preserved original is authoritative.|
|ADD04_JRC_ZERO_GRADIENT|CORE — independent hardware/flow-field electrochemical validation|Both manuscripts: current-density-dependent voltage, pressure/temperature/voltage distributions, EIS and KK-oriented comparison across two hardware configurations; test robustness of cell maps to hardware geometry.|Workbook uses multi-row/merged headers and must be imported with the supplied workbook inspector; single-cell hardware, not full stack/BoP.|
|ADD05_OXYGEN_PURGE|AUV-SPECIFIC SUPPORT — structured experimental DoE, not raw waveform|AUV manuscript: finite-O2 operation, purge-duration/interval, load-level, temperature and oxygen-utilization surrogate map; supports purge/inventory sensitivity and AIP mode feasibility studies.|Small structured experiment/training tables (not continuous raw time series); ANN code is a reproducibility aid, not automatically a validated plant model.|
|ADD06_NPL_CO_DIAGNOSTICS|SPECIALIZED HIGH-QUALITY SUPPORT — contamination diagnostics|High-quality PEMFC diagnostics: synchronized cell voltage/pressure with sparse CO/CO2 and high-rate isotope products/adsorbed-CO estimates; useful for contamination-state observers and recovery/diagnostic methodology.|Specialized trace-CO experiment, not representative of certified high-purity tank H2 or the main F-AAV/AUV operating map; independent time bases must not be row-joined.|

## 제외·보류 데이터

|후보|판정|이유|
|---|---|---|
|HAEOLUS Project fuel-cell data|REJECT|Ten tiny ts/value files are not sufficiently self-describing: authoritative units, test protocol and common clock/channel semantics are missing.|
|Loughborough 2018 PEMFC rig CSV|HOLD|Rich 24-channel data but contains invalid/sentinel channels (e.g. one temperature channel near −64,000) and undocumented startup/sensor-validity intervals. Not added until a verified quality mask and event/label ledger are constructed.|
|Loughborough 2016 practical fault data|HOLD|Institutional and real, but legacy workbook schema and labels are insufficiently explicit for immediate leakage-safe reuse; newer cleaner alternatives exist.|
|Two-system flooding/dehydration workbook|HOLD|Large dataset across two systems, but worksheet columns are grouped with ambiguous multi-row headers and no machine-readable channel/episode registry in the deposited file.|
|Flooding versus humidity-sensor-abnormality CSV|HOLD|Useful fault concept, but one implausible sensor column and insufficient explicit route/episode labels prevent strict admission without manual reconstruction.|
|AC voltage-response dataset|REJECT FOR THIS PACKAGE|Very large and narrowly focused; marginal benefit is low relative to already admitted EIS/fault resources, so it is not added merely because it is downloadable.|
|HAEOLUS/industrial non-PEMFC proxy data|REJECT|Not sufficiently specific or documented to calibrate the target PEMFC plant.|
|100 kW/250 kW mobility-module or integrated underwater-AIP operational raw data|NOT FOUND|No public raw dataset meeting the required synchronized stack+BoP+thermal+reactant+mode-transition quality was verified. D-class assumptions remain assumptions.|

## 결론

두 원고를 실측자료 기반으로 크게 강화할 수 있는 추가자료는 확보했습니다. 그러나 **2×250 kW F-AAV용 완전 PEMFC 시스템 지도**와 **잠항체용 폐쇄형 H₂/O₂ AIP의 start–stop–restart–thermal–reactant 통합 운전 RAW**는 공개자료에서 확인하지 못했습니다. 이 부분은 공개데이터로 대체하지 않고 불확정/D-class 또는 후속 자체시험으로 유지해야 합니다.
