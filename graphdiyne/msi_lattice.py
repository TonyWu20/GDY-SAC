"""
.msi file based model creation
"""
import re
from typing import Dict, List, Tuple
from pathlib import Path
import numpy as np
import yaml as y
import dpath.util as dp
from mendeleev import element


class MsiLattice:
    """
    Object of lattice model
    """
    def __init__(self, filepath: Path):
        """
        Args:
            filepath: Path of the lattice model
        """
        self.filepath = filepath
        self.metal = filepath.stem.split("_")[2]
        with open("castep_input/element_table.yaml", 'r') as file:
            self.table = y.full_load(file)
        self.metal_prop = dp.get(self.table, f'*/{self.metal}')
        self.spin = self.metal_prop['spin']
        self.text = filepath.read_text()

    def get_param_msi(self, direction: str):
        """
        Get lattice parameter a, b, or c
        Args:
            direction (str): a, b, or c
            text (str): msi file text
        return:
            param (np.float64)
        """
        assert direction in ["a", "b", "c"], "Only a, b or c"
        vector_re = {
            'a': re.compile(r"(?<=A3\s)\((.*)\)\)"),
            'b': re.compile(r"(?<=B3\s)\((.*)\)\)"),
            'c': re.compile(r"(?<=C3\s)\((.*)\)\)"),
        }
        vectors_str = vector_re[direction].search(self.text).group(1)
        vectors = [float(item) for item in vectors_str.split(" ")]
        return vectors

    @classmethod
    def find_atom_by_id(cls, atom_id: int) -> re.Pattern:
        """
        Get atom info by id.
        Groups:
            1: ACL
            2: Label
            3: XYZ
            4: Id
        """
        atom = (r'^  \([0-9]+ Atom\n'
                r'.*ACL "([0-9a-zA-Z ]+)"\)\n'
                r'.*Label "([a-zA-Z]+)"\)\n'
                r'.*XYZ \(([0-9 e.-]+)\).*\n.*'
                f'Id ({atom_id})'
                r'.*\n.*\)\n')
        atom_re = re.compile(atom, re.MULTILINE)
        return atom_re

    @property
    def lattice_vectors(self):
        """
        Return lattice vector strings
        """
        vector_re = {
            'a': re.compile(r"(?<=A3\s)\((.*)\)\)"),
            'b': re.compile(r"(?<=B3\s)\((.*)\)\)"),
            'c': re.compile(r"(?<=C3\s)\((.*)\)\)"),
        }
        vectors_str = [
            vector_re[direction].search(self.text).group(1)
            for direction in ["a", "b", "c"]
        ]

        def format_str(vec_str: str) -> str:
            """
            convert the vector string to array
            Args:
                vec_str: string of vector
            returns:
                arr : vector in array form
            """
            values = vec_str.split(' ')
            new_str = [f"{float(value):.15f}" for value in values]
            align_str = [f"{value:>18}" for value in new_str]
            line = "      ".join(align_str)
            return line

        vec_a, vec_b, vec_c = (
            format_str(item)  #type:ignore
            for item in vectors_str)
        return (vec_a, vec_b, vec_c)

    @property
    def current_atoms(self) -> List[str]:
        """
        Get current atoms in .msi file
        """
        block_atoms = re.compile(r'^  \([0-9]+.*\n.*\n.*\n.*\n.*\n.*\)\n',
                                 re.MULTILINE)
        atoms = block_atoms.findall(self.text)
        return atoms

    @property
    def carbon_coords(self) -> Dict[str, np.ndarray]:
        """
        Coordinates of the five carbon sites
        """
        carbon_id = [41, 42, 54, 53, 40]
        names = ["c1", "c2", "c3", "c4", "c5"]

        def carbon_xyz(cid: int):
            atom_re = self.find_atom_by_id(cid)
            xyz_str = atom_re.search(self.text).group(3)  #type: ignore
            xyz_array = np.array(list(xyz_str.split(" ")))
            xyz_array = np.asfarray(xyz_array, dtype='double')
            return xyz_array

        carbon_coords = {
            key: carbon_xyz(cid)
            for key, cid in zip(names, carbon_id)
        }
        return carbon_coords

    @property
    def metal_xyz(self):
        """
        Coordinate of the metal atom
        """
        metal_re = self.find_atom_by_id(73)
        xyz_str = metal_re.search(self.text).group(3)
        xyz_array = np.array(list(xyz_str.split(" ")))
        xyz_array = np.asfarray(xyz_array, "double")
        return xyz_array

    @property
    def rotation_vector(self):
        """
        Determine x or y to align with when putting molecules
        """
        theta = np.pi / 3
        cos, sin = np.cos(theta), np.sin(theta)
        rot_matrix = np.array([[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]])
        return rot_matrix

    @property
    def head_end_lines(self) -> Tuple[str, str]:
        """
        The header and ending lines in .msi files with atom information only
        """
        block_atoms = re.compile(r'^  \([0-9]+.*\n.*\n.*\n.*\n.*\n.*\)\n',
                                 re.MULTILINE)
        head, end = list(filter(None, block_atoms.split(self.text)))
        return head, end
