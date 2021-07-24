"""
Methods to compute coordinates of molecules
"""
import re
from pathlib import Path
from typing import Tuple, Dict, List
from collections import Counter
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

        def convert_coord(coord_string: str):
            return [float(item) for item in coord_string.split(" ")]

        atoms = np.array([np.array(convert_coord(item)) for item in coords])
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

    def assign_variables(self):
        """
        assign variables in perl scripts for loop.
        """
        suffix = ["_x", "_y", "_z"]
        atom_id = [f"{elm}{suf}" for elm in self.elm_list for suf in suffix]
        var_list = ["source"] + atom_id + ["output"]

        def format_varlist(var: str, num: int):
            """
            Produce formatted line in for loop
            """
            perl_var = f"${var}"
            line = f"    my {perl_var:<7} = $item->[{num}];\n"
            return line

        var_lines = [
            format_varlist(var, num) for num, var in enumerate(var_list)
        ]
        doc_var = [
            "    my " + "{:<7}".format("$doc") +
            " = $Documents{\"${source}\"};\n"
        ]
        return var_lines + doc_var

    def create_atoms(self):
        """
        Create atoms in perl scripts for loop.
        """
        def create_atom(atom_var: str):
            """
            Create atom line
            """
            element = atom_var[0]
            left_line = "    my $" + "{:<7}".format(atom_var) + " = "
            right_line = (
                f'$doc->CreateAtom( "{element}",\n'
                f'    \t$doc->FromFractionalPosition( Point( X => ${atom_var}_x, '
                f'Y => ${atom_var}_y, Z => ${atom_var}_z ) ) );\n')
            line = left_line + right_line
            return line

        lines = [create_atom(elm) for elm in self.elm_list]
        return lines


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
        lattice = GDYLattice(use_lattice)
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
        converted_coord = lattice.convert_xyz(mole_coord)
        implanted_coord = converted_coord + ads_pos[site]
        output: np.ndarray = np.round(implanted_coord.astype(np.float64), 6)
        return output

    def adsorbate_setup(self, use_lattice: Path, site: str = "Metal"):
        """
        Format the adsorbate coordinates into MS perl script lines
        """
        ad_coord = self.feed_lattice(use_lattice, site)
        flat_coord = ad_coord.flatten()
        parent_dirs = use_lattice.parents
        lattice_str = f"'../../{parent_dirs[1].name}/{parent_dirs[0].name}/{use_lattice.name}', "
        coord_strings = ", ".join([str(i) for i in flat_coord])
        line = f"\t[{lattice_str} {coord_strings}, '{use_lattice.stem}'],\n"
        return line

    def export_setup(self, site: str = "Metal"):
        """
        Export setup in perl scripts
        """
        begin_line = "    $doc->CalculateBonds;\n"
        export_msi = ('    $doc->Export("${output}_'
                      f'{self.mol.filepath.stem}_{site}.msi");\n')
        export_xsd = ('    $doc->Export("${output}_'
                      f'{self.mol.filepath.stem}_{site}.xsd");\n')
        end_line = "    $doc->Discard;\n    $doc->Close;\n}"
        result = [begin_line, export_msi, export_xsd, end_line]
        return result

    def build_actions(self, site: str = "Metal"):
        """
        Generate model building actions for the molecule in perl scripts
        """
        start_line = ["foreach my $item (@params) {\n"]
        var_lines = self.mol.assign_variables()
        atom_lines = self.mol.create_atoms()
        export_lines = self.export_setup(site)
        total = start_line + var_lines + atom_lines + export_lines
        return total
