"""
Data structure to process msi file
"""
from dataclasses import dataclass, field
from typing import List, Set, Dict
import periodictable as pdtable
import numpy as np
import msiProcessor.my_maths as my_maths


@dataclass(order=True)
class Atom:
    """
    Data structure for an atom in .msi
    """
    element: str
    x: float  # pylint: disable=invalid-name
    y: float  # pylint: disable=invalid-name
    z: float  # pylint: disable=invalid-name
    Id: int  # pylint: disable=invalid-name
    stem_atom: bool = field(init=False, repr=False)
    coord_atom: bool = field(init=False, repr=False)
    plane_atom: bool = field(init=False, repr=False)
    TreeId: int  # pylint: disable=invalid-name
    sort_index: int = field(init=False, repr=False)

    def __post_init__(self):
        self.sort_index = self.Id

    def __repr__(self) -> str:
        return f"Element: {self.element}\nCoord: [{self.x}, {self.y},\
                {self.z}]\nID in tree:{self.TreeId}\nAtom ID: {self.Id}"

    def get_coord(self) -> np.ndarray:
        """
        Return coord from x, y, z
        """
        return np.array([self.x, self.y, self.z], dtype='double')

    def text_in_msi(self) -> str:
        """
        Generate text in msi
        """
        atomic_number: int = 0 if self.element == "H" else pdtable.elements.symbol(
            self.element).number
        acl_line = f"{atomic_number} {self.element}"
        xyz_line = " ".join([f"{item:.12}" for item in self.get_coord()])
        atom_block = (f'  ({self.TreeId} Atom\n'
                      f'    (A C ACL "{acl_line}")\n'
                      f'    (A C Label "{self.element}")\n'
                      f'    (A D XYZ ({xyz_line}))\n'
                      f'    (A I Id {self.Id})\n  )\n')
        return atom_block

    def set_coord(self, coord_arr: np.ndarray) -> None:
        self.x = coord_arr[0]
        self.y = coord_arr[1]
        self.z = coord_arr[2]


@dataclass
class AdsMol:  # pylint:disable=too-many-instance-attributes
    """
    Data structure of molecule
    """
    name: str
    atom_table: Dict[int, Atom]
    anchor_site: int
    binding_site_number: int
    binding_site: List[int]
    stem_atom_list: List[int]
    plane_atom_list: List[int]
    element_set: Set[str] = field(init=False, repr=False)
    element_list: List[str] = field(init=False, repr=False)

    def __post_init__(self):
        self.update_mol_coords(self.make_upright())
        self.update_mol_coords(self.reset_origin())
        self.element_set = set(a.element for a in self.atom_table.values())
        self.element_list = [a.element for a in self.atom_table.values()]

    def get_atom_by_id(self, atom_id: int) -> Atom:
        """
        Return a single Atom object
        """
        return self.atom_table[atom_id]

    def get_coordinates(self):
        """
        Return coordinates of molecule atoms
        """
        coords = np.array([a.get_coord() for a in self.atom_table.values()],
                          dtype='double')
        return coords

    def reset_origin(self) -> np.ndarray:
        """
        Reset coordinates, anchor as origin
        """
        coords = self.get_coordinates()
        origin_atom = self.get_atom_by_id(self.anchor_site)
        origin_coord = np.array([origin_atom.x, origin_atom.y, origin_atom.z],
                                dtype='double')
        new_coord = coords - origin_coord
        return new_coord

    def update_mol_coords(self, new_coords: np.ndarray):
        """
        Update coords for the whole molecule
        """
        assert len(new_coords) == len(self.atom_table)
        for atom, coord in zip(self.atom_table.values(), new_coords):
            atom.set_coord(coord)

    def get_stem_vector(self) -> np.ndarray:
        """
        return stem vector
        """
        atom_1 = self.get_atom_by_id(self.stem_atom_list[0])
        atom_2 = self.get_atom_by_id(self.stem_atom_list[1])
        a1_coord = atom_1.get_coord()
        a2_coord = atom_2.get_coord()
        stem_vector: np.ndarray = a1_coord - a2_coord
        return stem_vector

    def make_upright(self) -> np.ndarray:
        """
        Set the molecule upright, parallel to the xz plane
        """
        p_a = self.get_atom_by_id(self.plane_atom_list[0])
        p_b = self.get_atom_by_id(self.plane_atom_list[1])
        p_c = self.get_atom_by_id(self.plane_atom_list[2])
        vec_ba: np.ndarray = p_b.get_coord() - p_a.get_coord()
        vec_ca: np.ndarray = p_c.get_coord() - p_a.get_coord()
        normal = np.cross(vec_ca, vec_ba)
        n_xz = np.array([0, 1, 0])
        unit_mol_N = normal / np.linalg.norm(normal)
        dot_product = np.dot(unit_mol_N, n_xz)
        angle = np.arccos(dot_product)
        rot_matrix = my_maths.rotation_matrix(-angle, 'x')
        mol_coords = self.get_coordinates()
        new_coords = np.dot(mol_coords, rot_matrix)
        return new_coords

    def export_msi(self):
        atom_blocks: List[str] = [
            atom.text_in_msi() for atom in self.atom_table.values()
        ]
        heading = "# MSI CERIUS2 DataModel File Version 4 0"
        ending = ")"
        text_lines: List[str] = [heading] + atom_blocks + [ending]
        for line in text_lines:
            print(line)
