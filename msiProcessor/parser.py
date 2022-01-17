import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Iterator, Dict, Tuple
import numpy as np
from msiProcessor.DataStructs import Atom, AdsMol, Lattice

mole_database = {
    "C2H4": {
        "coord_atoms": [1, 2],
        "stem_atoms": [1, 2],
        "plane_atoms": [1, 2, 3]
    },
    "COCHO": {
        "coord_atoms": [4],
        "stem_atoms": [3, 5],
        "plane_atoms": [3, 4, 5]
    },
    "COCHOH": {
        "coord_atoms": [4],
        "stem_atoms": [3, 5],
        "plane_atoms": [3, 4, 5]
    },
    "OCH2CO": {
        "coord_atoms": [2, 4],
        "stem_atoms": [2, 4],
        "plane_atoms": [3, 4, 5]
    },
    "OCH2COH": {
        "coord_atoms": [2, 4],
        "stem_atoms": [2, 4],
        "plane_atoms": [2, 3, 4]
    },
    "OCH2CHOH": {
        "coord_atoms": [2, 4],
        "stem_atoms": [2, 4],
        "plane_atoms": [2, 3, 4]
    },
    "OCH2CH": {
        "coord_atoms": [2, 4],
        "stem_atoms": [2, 4],
        "plane_atoms": [2, 3, 4]
    },
    "OCH2CH2": {
        "coord_atoms": [2, 4],
        "stem_atoms": [2, 4],
        "plane_atoms": [2, 3, 4]
    }
}


@dataclass
class Molecule:
    """
    Parse molecule files
    """
    filepath: Path
    name: str = field(init=False, repr=False)
    text: str = field(init=False, repr=False)
    info: dict = field(init=False, repr=False)
    atom_table: Dict[int, Atom] = field(init=False, repr=False)

    def __post_init__(self):
        """
        After initialization
        """
        self.text = self.filepath.read_text()
        self.name = self.filepath.stem
        self.atom_table = self.parse_atoms()
        self.assign_atom_roles()

    def build_atom(self, match_res: re.Match) -> Atom:
        """
        Build from match
        """
        tree_id = int(match_res.group(1))
        element = match_res.group(2)
        xyz: List[str] = match_res.group(3).split(" ")
        x = float(xyz[0])
        y = float(xyz[1])
        z = float(xyz[2])
        Id = int(match_res.group(4))
        new_atom = Atom(element, x, y, z, Id, tree_id)
        return new_atom

    def parse_atoms(self) -> Dict[int, Atom]:
        """
        Parse the files, return a list of atoms
        """
        atom = (r'^  \(([0-9]+) Atom\n'
                r'.*ACL "[0-9a-zA-Z ]+"\)\n'
                r'.*Label "([a-zA-Z]+)"\)\n'
                r'.*XYZ \(([0-9 e.-]+)\).*\n.*'
                r'Id ([0-9]+)'
                r'.*\n.*\)\n')
        atom_re = re.compile(atom, re.MULTILINE)
        atom_match: Iterator[re.Match] = atom_re.finditer(self.text)
        atom_list = [self.build_atom(m) for m in atom_match]
        atom_table = {a.Id: a for a in atom_list}
        return atom_table

    def assign_atom_roles(self):
        """
        Assign roles to atoms
        """
        info = mole_database[self.name]
        for i in info["coord_atoms"]:
            self.atom_table[i].coord_atom = True
        for i in info["stem_atoms"]:
            self.atom_table[i].stem_atom = True
        for i in info["plane_atoms"]:
            self.atom_table[i].plane_atom = True

    def build_AdsMol(self) -> AdsMol:
        """
        Export AdsMol object
        """
        info = mole_database[self.name]
        new_mol = AdsMol(self.name, self.atom_table, info["coord_atoms"][0],
                         len(info["coord_atoms"]), info["coord_atoms"],
                         info["stem_atoms"], info["plane_atoms"])
        return new_mol


def build_atom(match_res: re.Match) -> Atom:
    """
        Build from match
        """
    tree_id = int(match_res.group(1))
    element = match_res.group(2)
    xyz: List[str] = match_res.group(3).split(" ")
    x = float(xyz[0])
    y = float(xyz[1])
    z = float(xyz[2])
    Id = int(match_res.group(4))
    new_atom = Atom(element, x, y, z, Id, tree_id)
    return new_atom


def parse_atoms(text: str) -> Dict[int, Atom]:
    """
    Parse the files, return a list of atoms
    """
    atom = (r'^  \(([0-9]+) Atom\n'
            r'.*ACL "[0-9a-zA-Z ]+"\)\n'
            r'.*Label "([a-zA-Z]+)"\)\n'
            r'.*XYZ \(([0-9 e.-]+)\).*\n.*'
            r'Id ([0-9]+)'
            r'.*\n.*\)\n')
    atom_re = re.compile(atom, re.MULTILINE)
    atom_match: Iterator[re.Match] = atom_re.finditer(text)
    atom_list = [build_atom(m) for m in atom_match]
    atom_table = {a.Id: a for a in atom_list}
    return atom_table


def get_lattice_vector(text) -> np.ndarray:
    """
    Parse text to extract the lattice vector
    """
    vec_re_a = re.compile(r"(?<=A3\s)\((.*)\)\)")
    vec_re_b = re.compile(r"(?<=B3\s)\((.*)\)\)")
    vec_re_c = re.compile(r"(?<=C3\s)\((.*)\)\)")
    va_str = vec_re_a.search(text).group(1)
    vb_str = vec_re_b.search(text).group(1)
    vc_str = vec_re_c.search(text).group(1)
    vectors = []
    for vec_str in [va_str, vb_str, vc_str]:
        vectors.append([float(item) for item in vec_str.split(" ")])

    vectors = np.array(vectors)
    return vectors


def parse_lattice(lattice_path: Path) -> Lattice:
    """
    Parse imported msi file into a lattice object
    """
    file = lattice_path
    name = file.stem
    metal = name.split("_")[-1]
    text = file.read_text()
    atom_table = parse_atoms(text)
    lattice_vec = get_lattice_vector(text)
    lat_obj = Lattice(name, metal, lattice_vec, atom_table)
    return lat_obj