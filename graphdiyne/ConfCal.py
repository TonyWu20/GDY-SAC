"""
Methods to compute coordinates of molecules
"""
import re
from pathlib import Path
from typing import Tuple, Dict
import numpy as np
import sympy as sp
from graphdiyne.lattice import GDYLattice


class Molecule:
    """
    Parse molecule model file to get coordinates
    """
    def __init__(self, filepath: Path):
        """
        Args:
            filepath: path of the molecule model (.msi)
        """
        assert filepath.suffix == ".msi", "Wrong format of model (not msi)!"
        self.filepath = filepath
        self.__text = filepath.read_text()

    @property
    def elements(self):
        """
        Return elements of molecule atoms in order
        """
        atom_elm = re.compile(r"ACL \"\d+ (\w+)\"")
        elm_list = atom_elm.findall(self.__text)
        return elm_list

    @property
    def coordinates(self):
        """
        Return coordinates of molecule atoms
        """
        xyz = re.compile(r"XYZ\s\((.*)\)\)")
        coords = xyz.findall(self.__text)

        def convert_coord(coord_string: str):
            return [float(item) for item in coord_string.split(" ")]

        atoms = np.array([np.array(convert_coord(item)) for item in coords])
        atoms_origin = atoms - atoms[0]
        return atoms_origin


class ModelFactory:
    """
    Assemble one molecule to many lattice models
    """
    def __init__(self, use_mol: Path, mol_height):
        """
        Init factory by feeding the target molecule
        """
        self.mol = Molecule(use_mol)
        self.mol_height = mol_height

    def feed_lattice(self, use_lattice: Path) -> np.ndarray:
        """
        Place the target molecule to input lattices
        Args:
            use_lattice (Path): path of the target lattice
            mol_height (float): height of the molecule
        returns:
            output (np.ndarray): arrays of the molecule atoms coordinates
        """
        lattice = GDYLattice(use_lattice)
        push_height = np.array([0, 0, self.mol_height])
        mole_coord = np.dot(self.mol.coordinates + push_height,
                            lattice.rotation_vector)
        converted_coord = lattice.convert_xyz(mole_coord)
        implanted_coord = converted_coord + lattice.metal_xyz
        output: np.ndarray = np.round(implanted_coord.astype(np.float64), 6)
        return output

    def adsorbate_setup(self, use_lattice: Path):
        """
        Format the adsorbate coordinates into MS perl script lines
        """
        ad_coord = self.feed_lattice(use_lattice)
        flat_coord = ad_coord.flatten()
        parent_dirs = use_lattice.parents
        lattice_str = f"'../{parent_dirs[1].name}/{parent_dirs[0].name}/{use_lattice.name}', "
        coord_strings = ", ".join([str(i) for i in flat_coord])
        line = f"\t[{lattice_str} {coord_strings}, '{use_lattice.stem}'],\n"
        return line
