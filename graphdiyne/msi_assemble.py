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
from graphdiyne.msi_lattice import MsiLattice


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
    def __init__(self, use_mol: Path, mol_height, lattices_dir: Path,
                 site: str):
        """
        Init factory by feeding the target molecule
        """
        self.mol = Molecule(use_mol)
        self.mol_height = mol_height
        self.site = site
        self.outdir = Path(self.mol.dest + f"_{lattices_dir.name}/" +
                           lattices_dir.name +
                           f"_{self.mol.filepath.stem}/{site}")
        if not self.outdir.exists():
            self.outdir.mkdir(parents=True)

    @classmethod
    def build_atom(cls, atom_elm: str, atom_xyz: np.ndarray,
                   atom_id: int) -> str:
        """
        Construct atom blocks in .msi file
        """
        current_id = 73 + atom_id + 1
        atomic_number = element(atom_elm).atomic_number
        acl_prop = f"{atomic_number} {atom_elm}"
        xyz_string = " ".join([f"{item:.12}" for item in atom_xyz])
        atom = (f'  ({current_id+1} Atom\n'
                f'    (A C ACL "{acl_prop}")\n'
                f'    (A C Label "{atom_elm}")\n'
                f'    (A D XYZ ({xyz_string}))\n'
                f'    (A I Id {current_id})\n  )\n')
        return atom

    def place_mol(self, use_lattice: Path) -> np.ndarray:
        """
        Place the target molecule to input lattices
        Args:
            use_lattice (Path): path of the target lattice
            site (str): adsorption site
        returns:
            output (np.ndarray): arrays of the molecule atoms coordinates
        """
        lattice = MsiLattice(use_lattice)
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
        implanted_coord: np.ndarray = mole_coord + ads_pos[self.site]
        return implanted_coord

    def assemble_mol(self, use_lattice: Path):
        """
        Generate new .msi file with adsorbate
        Args:
            use_lattice (Path): path of the target lattice
            site (str): adsorption site
        """
        lattice = MsiLattice(use_lattice)
        adsorbate_atoms = [
            self.build_atom(elm, coord, use_id) for elm, coord, use_id in zip(
                self.mol.elements, self.place_mol(use_lattice),
                range(len(self.mol.elements)))
        ]
        all_atoms = ''.join(lattice.current_atoms + adsorbate_atoms)
        head, end = lattice.head_end_lines
        contents = head + all_atoms + end
        filename = "_".join([
            lattice.filepath.stem, self.mol.filepath.stem, self.site
        ]) + ".msi"
        with open(self.outdir / filename, 'w') as output:
            output.write(contents)
