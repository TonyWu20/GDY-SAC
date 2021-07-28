"""
Methods to compute coordinates of molecules
"""
import re
from pathlib import Path
from typing import Tuple, Dict, List
from collections import Counter
import numpy as np
import sympy as sp
from mendeleev import element
from castep_input.msicell import msiLattice


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
        self.dest = filepath.parent.name

    @property
    def elements(self) -> List[str]:
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
        atoms = np.array([np.array(list(item.split(" "))) for item in coords])
        atoms = np.asfarray(atoms, "double")
        atoms_origin = atoms - atoms[0]
        return atoms_origin

    @property
    def elm_list(self):
        """
        Return coordinates with elements. Progressive numbered when repeated
        elements exist.
        """
        elements = self.elements

        def solve_dup(mylist: list):
            counts = {k: v for k, v in Counter(mylist).items() if v > 1}
            for i in reversed(range(len(mylist))):
                item = mylist[i]
                if item in counts and counts[item]:
                    mylist[i] += str(counts[item])
                    counts[item] -= 1
            return mylist

        element_list = solve_dup(elements)
        return element_list


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

    def feed_lattice(self, use_lattice: Path, site: str) -> np.ndarray:
        """
        Place the target molecule to input lattices
        Args:
            use_lattice (Path): path of the target lattice
            mol_height (float): height of the molecule
        returns:
            output (np.ndarray): arrays of the molecule atoms coordinates
        """
        lattice = msiLattice(use_lattice)
        ads_pos = {
            "metal": lattice.metal_xyz,
            "c1": lattice.carbon_coords["c1"],
            "c2": lattice.carbon_coords["c2"],
            "c3": lattice.carbon_coords["c3"],
            "c4": lattice.carbon_coords["c4"],
            "c5": lattice.carbon_coords["c5"]
        }
        push_height = np.array([0, 0, self.mol_height])
        mole_coord = np.dot(self.mol.coordinates + push_height,
                            lattice.rotation_vector)
        implanted_coord: np.ndarray = mole_coord + ads_pos[site]
        return implanted_coord

    def build_atom(self, atom_elm: str, atom_xyz: np.ndarray,
                   atom_id: int) -> str:
        """
        Construct atom blocks in .msi file
        """
        current_id = 73 + atom_id
        atomic_number = element(atom_elm).atomic_number
        acl_prop = f"{atomic_number} {atom_elm}"
        xyz_string = " ".join([f"{item:.12}" for item in atom_xyz])
        atom = (f'  ({current_id+1} Atom\n'
                f'    (A C ACL "{acl_prop}")\n'
                f'    (A C Label "{atom_elm}")\n'
                f'    (A D XYZ ({xyz_string}))\n'
                f'    (A I Id {current_id})\n  )\n')
        return atom
