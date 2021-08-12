"""
.msi file based model creation
"""
import re
from typing import Dict, List, Tuple, Optional
from itertools import chain
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
    def atom_re_pat(cls) -> re.Pattern:
        """
        Atom regex pattern
        """
        atom = (r'^  \([0-9]+ Atom\n'
                r'.*ACL "([0-9a-zA-Z ]+)"\)\n'
                r'.*Label "([a-zA-Z]+)"\)\n'
                r'.*XYZ \(([0-9 e.-]+)\).*\n.*'
                f'Id ([0-9]+)'
                r'.*\n.*\)\n')
        atom_re = re.compile(atom, re.MULTILINE)
        return atom_re

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

    @classmethod
    def find_atom_by_elm(cls, elm: str) -> re.Pattern:
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
                f'.*Label "({elm})"\)\n'
                r'.*XYZ \(([0-9 e.-]+)\).*\n.*'
                r'Id ([0-9]+)'
                r'.*\n.*\)\n')
        atom_re = re.compile(atom, re.MULTILINE)
        return atom_re

    @property
    def lat_params(self) -> tuple:
        """
        Get lattice params
        """
        vectors = self.vector_arrays
        lat_params = tuple(np.linalg.norm(vec) for vec in vectors)
        a, b, c = lat_params
        return (a, b, c)  #type: ignore

    @property
    def vector_arrays(self) -> List[np.ndarray]:
        """
        Return lattice vector arrays
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
        vectors: List[np.ndarray] = [
            np.double(item.split(" ")) for item in vectors_str
        ]
        return vectors

    @property
    def lattice_vectors(self) -> tuple:
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

    @property
    def elements(self) -> List[str]:
        """
        Return existing elements, sorted by atomic number
        """
        atom_re = self.atom_re_pat()
        elements = set(item.group(2) for item in atom_re.finditer(self.text))
        sorted_elements = sorted(list(elements),
                                 key=lambda x: element(x).atomic_number)
        return sorted_elements

    @property
    def element_masses(self) -> List[str]:
        """
        Get element masses
        return:
            mass_lines: formatted list of lines about element mass for output
        """
        elements = self.elements
        aligned_elements = [f"      {item:>2}" for item in elements]
        masses = [dp.get(self.table, f'*/{elm}')['mass'] for elm in elements]
        masses = [f"{float(item):.10f}" for item in masses]
        aligned_masses = [f"{item:>15}\n" for item in masses]
        mass_lines = [
            elm + "   " + mass
            for elm, mass in zip(aligned_elements, aligned_masses)
        ]
        return mass_lines

    @property
    def potential_files(self) -> List[str]:
        """
        Get the specified pseudopotential files of the elements.
        returns:
            pot_lines: formatted list of strings about potential files
        """
        elements = self.elements
        aligned_elements = [f"      {item:>2}" for item in elements]
        pots = [dp.get(self.table, f"*/{elm}")['pot'] for elm in elements]
        pot_lines = [
            elm + "  " + pot + "\n"
            for elm, pot in zip(aligned_elements, pots)
        ]
        return pot_lines

    @property
    def LCAO_states(self) -> List[str]:  #pylint: disable=invalid-name
        """
        Get the LCAO states of elements
        returns:
            lcao_lines: formatted list of strings about LCAO states
        """
        elements = self.elements
        aligned_elements = [f"      {item:>2}" for item in elements]
        lcao_values = [
            dp.get(self.table, f"*/{elm}")['LCAO'] for elm in elements
        ]
        lcao_strings = [str(value) for value in lcao_values]
        lcao_lines = [
            elm + "         " + lcao + "\n"
            for elm, lcao in zip(aligned_elements, lcao_strings)
        ]
        return lcao_lines

    @property
    def castep_dir(self):
        """
        Directory to put input files
        """
        stem = self.filepath.stem
        if not "opt" in self.filepath.parent.name:
            castep_dir = self.filepath.parent / f"{stem}_opt"
            if not castep_dir.exists():
                castep_dir.mkdir(parents=True)
        else:
            castep_dir = self.filepath.parent
        return castep_dir

    def get_atomid_by_elm(self, elm) -> List[Optional[str]]:
        """
        Get atom id(s) for input elements.
        Args:
            elm (str): elements
        """
        elm_pattern = self.find_atom_by_elm(elm)
        atom_ids = [item.group(4) for item in elm_pattern.finditer(self.text)]
        return atom_ids

    @property
    def atom_ids_by_elm(self) -> List[Optional[str]]:
        """
        All atom ids sorted in atomic number. For .trjaux file use.
        """
        elements = self.elements
        res = [self.get_atomid_by_elm(elm) for elm in elements]
        atom_ids = list(chain.from_iterable(res))
        return atom_ids

    def coord_to_frac(self, real_coords: np.ndarray) -> np.ndarray:
        """
        Convert real coords in .msi to frac coord for .cell
        """
        a, b = self.lat_params[:2]  #pylint: disable=invalid-name
        vec_a, vec_b, vec_c = self.vector_arrays  #type:ignore
        vol = np.dot(vec_a, np.cross(vec_b, vec_c))
        cos_y = np.cos(np.pi * 2 / 3)
        sin_y = np.sin(np.pi * 2 / 3)
        trans_matrix = np.array(
            [[1 / (a * sin_y), -1 * cos_y / (a * sin_y), 0], [0, 1 / b, 0],
             [0, 0, a * b * sin_y / vol]])
        frac: np.ndarray = np.dot(real_coords, trans_matrix)
        return frac

    def format_atom_xyz(self, xyz_item: np.ndarray, elm: str):
        """
        Format atom xyz with element information into a line of strings
        """
        # 16 decimal digits
        align_str = [f"{val:>19.16f}" for val in xyz_item]
        # Right align strings
        formatted_xyz = "  ".join(align_str)
        if elm == self.metal and self.spin != 0:
            line = f" {elm:>2}  {formatted_xyz} SPIN=  {self.spin:.10f}\n"
        else:
            line = f" {elm:>2}  {formatted_xyz}\n"
        return line
