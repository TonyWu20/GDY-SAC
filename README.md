# GDY-SAC

Python and perl scripts to assist tasks in GDY-SAC and CO2RR adsorption modelling.

## Usage

1. gen_ads_model.py

   - mode:

   1. model: Generate adsorbate attached models in .msi format
   2. to_xsd: Generate perl script to be executed by Materials Studio, generating .xsd format files.

2. gen_castep_seed.py: Generate necessary input files for running CASTEP. Including:

   1. \*.param and \*\_DOS.param : parameter files of CASTEP.
   2. \*.cell and \*\_DOS.cell : structure input files for CASTEP.
   3. \*.trjaux and \*.kptaux: trajectory auxiliary files and k-point auxiliary files.
   4. Copy corresponding potential files into the directory.
   5. Generate the CASTEP setting xml file (SMCASTEP\*.xms)
   6. Generate the pbs queuing system script (hpc.pbs.sh)

3. get_cellinfo.py: Extract necessary information in .cell file of the metal elements. For reuse in gen_castep_seed.py

4. create_model.py: Modify the metal element in the template SAC_GDY_Sc.xsd to create the GDY SAC models with various metal elements.

## Adsorbates (C1 Pathway)

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

## Adsorbates C2 pathway

![C2_path](Figures/C2_path.jpg)

> ACS Catal. 2018, 8, 2, 1490–1499.

- General
  - [x] CO
  - [x] CHO
  - [ ] COCHO
- [ ] Ethylene Path
  - [ ] COCHOH (radical)
  - [ ] OCCH2O
  - [ ] HOCCH2O
    - [ ] OH-(CCH2O)
    - [ ] CH3COOH (Acetic Acid)
  - [ ] HOCHCH2O
  - [ ] HCCH2O
  - [ ] 

## Done: CASTEP input files generation (2021-08-06)

Workflow:

1. Molecule insertion scripts: generate adsorption structure msi
2. Generate .cell file: Coordinates, important settings, **specification of potential files**, LCAO
   - Construct table for:
     1. Element Spin
     2. Corresponding potential files
     3. LCAO setting
     4. Mass
3. Generate .param file:
   - Modifications:
     1. cut_off_energy: depends on the highest value from potential files. 1.1\* fine
     2. nextra_band: change to perc_extra_bands
     3. Spin: corresponds to the .cell
4. Run get_potentials.py and write_pbs_scripts.py
