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
from castep_input.CellGenerator import CellFile, DOSCellFile
from castep_input.ParamGenerator import ParamFile, MiscFile


def generate_cell(xsd_path: Path):
    """
    Generate .cell and dos.cell file for CASTEP input
    Args:
        xsd_path (Path): Path object of xsd file
    """
    cell = CellFile(xsd_path)
    cell_DOS = DOSCellFile(xsd_path)
    cell.write_cell()
    cell_DOS.write_cell()


def generate_param(xsd_path: Path):
    """
    Generate .param and dos.param for CASTEP input
    Args:
        xsd_path (Path): Path object of xsd file
    """
    param = ParamFile(xsd_path)
    misc = MiscFile(xsd_path)
    param.write_param()
    param.write_dos_param()
    param.copy_potentials()
    param.write_pbs_scripts()
    misc.write_kptaux()
    misc.write_trjaux()
    misc.copy_smcastep()


def main(xsd_pattern: str):
    """
    Main function to execute
    """
    root = Path.cwd()
    files = list(root.rglob(xsd_pattern))
    p_map(generate_cell, files)
    p_map(generate_param, files)


if __name__ == "__main__":
    Fire(main)
