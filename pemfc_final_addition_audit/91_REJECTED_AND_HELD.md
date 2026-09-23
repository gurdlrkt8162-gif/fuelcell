# 제외·보류 후보

## HAEOLUS Project fuel-cell data
- 판정: **REJECT**
- 이유: Ten tiny ts/value files are not sufficiently self-describing: authoritative units, test protocol and common clock/channel semantics are missing.

## Loughborough 2018 PEMFC rig CSV
- 판정: **HOLD**
- 이유: Rich 24-channel data but contains invalid/sentinel channels (e.g. one temperature channel near −64,000) and undocumented startup/sensor-validity intervals. Not added until a verified quality mask and event/label ledger are constructed.

## Loughborough 2016 practical fault data
- 판정: **HOLD**
- 이유: Institutional and real, but legacy workbook schema and labels are insufficiently explicit for immediate leakage-safe reuse; newer cleaner alternatives exist.

## Two-system flooding/dehydration workbook
- 판정: **HOLD**
- 이유: Large dataset across two systems, but worksheet columns are grouped with ambiguous multi-row headers and no machine-readable channel/episode registry in the deposited file.

## Flooding versus humidity-sensor-abnormality CSV
- 판정: **HOLD**
- 이유: Useful fault concept, but one implausible sensor column and insufficient explicit route/episode labels prevent strict admission without manual reconstruction.

## AC voltage-response dataset
- 판정: **REJECT FOR THIS PACKAGE**
- 이유: Very large and narrowly focused; marginal benefit is low relative to already admitted EIS/fault resources, so it is not added merely because it is downloadable.

## HAEOLUS/industrial non-PEMFC proxy data
- 판정: **REJECT**
- 이유: Not sufficiently specific or documented to calibrate the target PEMFC plant.

## 100 kW/250 kW mobility-module or integrated underwater-AIP operational raw data
- 판정: **NOT FOUND**
- 이유: No public raw dataset meeting the required synchronized stack+BoP+thermal+reactant+mode-transition quality was verified. D-class assumptions remain assumptions.
