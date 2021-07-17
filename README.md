# GDY-SAC

Python and perl scripts to assist tasks in GDY-SAC and CO2RR adsorption modelling.

## Adsorbates

![C1_path](figures/C1_path.jpg)
![adsorbates](figures/adsorbate.jpg)

### Path (i) and (vi)

- [x] CO2
- [x] COOH
- [x] CO
- [x] CHO
- [x] CH2O
- [x] CH3O
- [x] CH3OH

### Path (ii)

- [x] HCOO
- [x] HCOOH

### Path (vii)

- [x] COH
- [x] CHOH
- [x] CH2OH
- [x] C
- [x] CH
- [x] CH2
- [x] CH3
- [x] CH4

### HER

- [x] O
- [x] OH
- [x] H2O

## Bug log

### 2021/07/17

Wrong atom order in msi files, causing undesired adsorption contact position of the molecules.

Checked fine: HCOOH, HCOO

Fix:

- [ ] CH2
- [ ] CH3
- [ ] CH4
- [ ] CH3OH
