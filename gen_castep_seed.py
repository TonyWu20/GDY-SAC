"""
Generate castep input files from .xsd structure file.
Files:
    *.cell
    *_DOS.cell
    *.param
    *_DOS.param
    *.kptaux
    *_DOS.kptaux
    *.trjaux
    SMCASTEP_*.xms
"""
from pathlib import Path
from p_tqdm import p_map
from fire import Fire
from castep_input.CellGenerator_msi import CellFile, DOSCellFile
from castep_input.ParamGenerator_msi import ParamFile, MiscFile


def generate_cell(msi_path: Path):
    """
    Generate .cell and dos.cell file for CASTEP input
    Args:
        xsd_path (Path): Path object of xsd file
    """
    cell = CellFile(msi_path)
    cell_DOS = DOSCellFile(msi_path)
    cell.write_cell()
    cell_DOS.write_cell()


def generate_param(msi_path: Path):
    """
    Generate .param and dos.param for CASTEP input
    Args:
        xsd_path (Path): Path object of xsd file
    """
    param = ParamFile(msi_path)
    misc = MiscFile(msi_path)
    param.write_param()
    param.write_dos_param()
    param.copy_potentials()
    param.write_pbs_scripts()
    misc.write_kptaux()
    misc.write_trjaux()
    misc.copy_smcastep()
    misc.move_structures()


def main(msi_pattern: str):
    """
    Main function to execute
    """
    root = Path.cwd()
    files = list(root.rglob(msi_pattern))
    p_map(generate_cell, files)
    p_map(generate_param, files)


if __name__ == "__main__":
    Fire(main)
