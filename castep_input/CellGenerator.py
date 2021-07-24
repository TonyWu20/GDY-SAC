"""
Class objects about .cell file generations.
"""
import xml.etree.ElementTree as ET
from typing import Tuple, List
from pathlib import Path
import yaml as y
import dpath.util as dp
from mendeleev import element


class GDYLattice:
    """
    Object of gdy lattice
    """
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.tree = ET.parse(self.filepath)
        self.metal = filepath.stem.split("_")[2]
        with open("castep_input/element_table.yaml", 'r') as file:
            self.table = y.full_load(file)
        self.metal_prop = dp.get(self.table, f'*/{self.metal}')
        self.spin = self.metal_prop['spin']

    @property
    def lat_vectors(self) -> Tuple[str, str, str]:
        """
        lattice vectors in xsd file
        """
        lat_info = self.tree.find('.//SpaceGroup')
        str_a, str_b, str_c = (
            lat_info.get(key)  #type:ignore
            for key in ['AVector', 'BVector', 'CVector'])

        def format_str(vec_str: str) -> str:
            """
            format the vector value to specified decimals and alignments
            Args:
                vec_str: string of vector
            returns:
                line : formatted vector values
            """
            values = vec_str.split(',')
            new_str = [f"{float(value):.15f}" for value in values]
            align_str = [f"{value:>18}" for value in new_str]
            line = "      ".join(align_str)
            return line

        vec_a, vec_b, vec_c = (
            format_str(item)  #type:ignore
            for item in [str_a, str_b, str_c])
        return (vec_a, vec_b, vec_c)

    @property
    def elements(self) -> List[str]:
        """
        Elements in the lattice
        returns:
            elements: sorted by atomic number
        """
        atoms = self.tree.findall('.//Atom3d')
        res = set(atom.get("Components") for atom in atoms)
        elements: List[str] = [
            item for item in res  #type:ignore
            if item is not None
        ]
        elements.sort(key=lambda x: element(x).atomic_number  #type:ignore
                      )  #sort by element atomic number
        return elements

    def get_frac_by_elm(self, elm) -> List[str]:
        """
        Get fractional coords of atoms of input element
        Args:
            elm (str): Element name
        returns:
            frac_lines (str): list of fractional coords strings lines
        """
        atoms = self.tree.findall(f'.//Atom3d[@Components="{elm}"]')

        def get_frac(atom: ET.Element):
            """
            Get fractional coord of the atom
            Arg:
                atom (ET.element): ElementTree element (Atom3d)
            returns:
                line: 'Element' 'frac_coord'
            """
            xyz: str = atom.get("XYZ")  #type:ignore

            def format_xyz(xyz: str):
                """
                Format xyz str
                Args:
                    xyz: coord string
                return:
                    formatted_xyz: formatted string
                """
                values = xyz.split(",")
                new_str = [f"{float(value):.16f}" for value in values]
                align_str = [f"{value:>19}" for value in new_str]
                formatted_xyz = "  ".join(align_str)
                return formatted_xyz

            elm = atom.get("Components")
            if elm == self.metal and self.spin != 0:
                line = f" {elm:>2}  " + format_xyz(
                    xyz) + f" SPIN=  {self.spin:.10f}\n"
            else:
                line = f" {elm:>2}  " + format_xyz(xyz) + "\n"
            return line

        lines = [get_frac(atm) for atm in atoms]
        return lines

    @property
    def all_frac_coords(self) -> List[str]:
        """
        All atom fractional coords. Sorted by atomic number.
        returns:
            frac_lines: formatted list of strings of fractional coords
        """
        elements = self.elements
        frac_lines = [self.get_frac_by_elm(elm) for elm in elements]
        flattened_lines: List[str] = [
            item for line_list  #type:ignore
            in frac_lines for item in line_list
        ]
        return flattened_lines

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


class CellFile(GDYLattice):
    """
    Subclass of GDYLattice to generate .cell file
    """
    @classmethod
    def write_block(cls, block_name: str, content_lines: list) -> List[str]:
        """
        Method to write block sections in .cell
        Args:
            block_name (str): name of the block
            content_lines (list): lines in the block
        """
        begin = [f"%BLOCK {block_name}\n"]
        end = [f"%ENDBLOCK {block_name}\n\n"]
        block = begin + content_lines + end
        return block

    def block_lattice(self) -> List[str]:
        """
        LATTICE_CART block
        returns:
            lat_block: About the lattice vectors
        """
        vector_strings = self.lat_vectors
        vector_lines = ["      " + line + "\n" for line in vector_strings]
        lat_block = self.write_block("LATTICE_CART", vector_lines)
        return lat_block

    def block_frac(self) -> List[str]:
        """
        POSITIONS_FRAC block
        returns:
            block: About the atom fractional coords in the lattice. With SPIN if necessary
        """
        lines = self.all_frac_coords
        block = self.write_block("POSITIONS_FRAC", lines)
        return block

    def block_misc(self) -> List[str]:
        """
        Write common settings in .cell
        returns:
            misc: misc settings block. Not affected by elements.
        """
        kpoints = [
            "   0.0000000000000000   0.0000000000000000   0.0000000000000000       1.000000000000000\n"
        ]
        kpoint_list = self.write_block("KPOINTS_LIST", kpoints)
        line1 = ["FIX_ALL_CELL : true\n\n"]
        line2 = [
            "FIX_COM : false\n", "%BLOCK IONIC_CONSTRAINTS\n",
            "%ENDBLOCK IONIC_CONSTRAINTS\n\n"
        ]
        efield = ["    0.0000000000     0.0000000000     0.0000000000 \n"]
        external_efield = self.write_block("EXTERNAL_EFIELD", efield)
        pressure_1 = "    0.0000000000    0.0000000000    0.0000000000\n"
        pressure_2 = "                    0.0000000000    0.0000000000\n"
        pressure_3 = "                                    0.0000000000\n"
        pressure = self.write_block("EXTERNAL_PRESSURE",
                                    [pressure_1, pressure_2, pressure_3])
        misc = kpoint_list + line1 + line2 + external_efield + pressure
        return misc

    def block_masses(self) -> List[str]:
        """
        SPECIES_MASS block
        returns:
            mass_block: masses of the elements in the lattice.
        """
        mass_lines = self.element_masses
        mass_block = self.write_block("SPECIES_MASS", mass_lines)
        return mass_block

    def block_pot(self) -> List[str]:
        """
        SPECIES_POT block
        returns:
            pot_block: potential files to use in the lattice
        """
        pot_lines = self.potential_files
        pot_block = self.write_block("SPECIES_POT", pot_lines)
        return pot_block

    def block_LCAO(self) -> List[str]:  #pylint:disable=invalid-name
        """
        SPECIES_LCAO_STATES block
        returns:
            lcao_block: the LCAO states of the elements in the lattice
        """
        lcao_lines = self.LCAO_states
        lcao_block = self.write_block("SPECIES_LCAO_STATES", lcao_lines)
        return lcao_block

    def write_cell(self):
        """
        Write blocks to .cell file
        """
        stem = self.filepath.stem
        cellfile = self.filepath.parent / f"{stem}_test.cell"
        contents = [
            self.block_lattice(),
            self.block_frac(),
            self.block_misc(),
            self.block_masses(),
            self.block_pot(),
            self.block_LCAO()
        ]
        with open(cellfile, 'w', newline='\r\n') as file:
            for item in contents:
                file.writelines(item)


class DOSCellFile(CellFile):
    """
    *DOS.cell file. Subclass of CellFile.
    """
    def block_misc(self) -> List[str]:
        """
        Write common settings in .cell
        returns:
            misc: misc settings block. Not affected by elements.
        """
        kpoints = [
            "   0.0000000000000000   0.0000000000000000   0.0000000000000000       1.000000000000000\n"
        ]
        bskpoint_list = self.write_block("BS_KPOINT_LIST", kpoints)
        kpoint_list = self.write_block("KPOINTS_LIST", kpoints)
        line1 = ["FIX_ALL_CELL : true\n\n"]
        line2 = [
            "FIX_COM : false\n", "%BLOCK IONIC_CONSTRAINTS\n",
            "%ENDBLOCK IONIC_CONSTRAINTS\n\n"
        ]
        efield = ["    0.0000000000     0.0000000000     0.0000000000 \n"]
        external_efield = self.write_block("EXTERNAL_EFIELD", efield)
        pressure_1 = "    0.0000000000    0.0000000000    0.0000000000\n"
        pressure_2 = "                    0.0000000000    0.0000000000\n"
        pressure_3 = "                                    0.0000000000\n"
        pressure = self.write_block("EXTERNAL_PRESSURE",
                                    [pressure_1, pressure_2, pressure_3])
        misc = bskpoint_list + kpoint_list + line1 + line2 + external_efield + pressure
        return misc

    def write_cell(self):
        """
        Write blocks to .cell file
        """
        stem = self.filepath.stem
        castep_dir = self.filepath.parent / f"{stem}_opt"
        if not castep_dir.exists():
            castep_dir.mkdir(parents=True)
        cellfile = castep_dir / f"{stem}_DOS_test.cell"
        contents = [
            self.block_lattice(),
            self.block_frac(),
            self.block_misc(),
            self.block_masses(),
            self.block_pot(),
            self.block_LCAO()
        ]
        with open(cellfile, 'w', newline='\r\n') as file:
            for item in contents:
                file.writelines(item)
