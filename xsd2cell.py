"""
Convert .xsd file to .cell
"""
import xml.etree.ElementTree as ET
from typing import Tuple, List
from pathlib import Path
import yaml as y
import dpath.util as dp
from mendeleev import element
from p_tqdm import p_map
from fire import Fire
from castep_input.CellGenerator import CellFile, DOSCellFile


def generate_cell(xsd_path: Path):
    """
    Generate .cell file for CASTEP input
    Args:
        xsd_path (Path): Path object of xsd file
    """
    cell = CellFile(xsd_path)
    cell_DOS = DOSCellFile(xsd_path)
    cell.write_cell()
    cell_DOS.write_cell()


def main(xsd_pattern: str):
    """
    Main function to execute
    """
    root = Path.cwd()
    files = list(root.rglob(xsd_pattern))
    p_map(generate_cell, files)


if __name__ == "__main__":
    Fire(main)
