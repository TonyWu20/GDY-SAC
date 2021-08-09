"""
Class objects about .cell file generations.
"""
from typing import List
import numpy as np
from graphdiyne.msi_lattice import MsiLattice


class CellFile(MsiLattice):
    """
    Subclass of GDYLattice to generate .cell file
    """
    @property
    def elm_frac_coords(self) -> List[str]:
        """
        lines of elements and frac coords of the atoms
        """
        def get_coords_by_elm(elm: str) -> np.ndarray:
            """
            get atom coords by element
            """
            real_xyz_str = [
                item.group(3)
                for item in self.find_atom_by_elm(elm).finditer(self.text)
            ]
            real_xyz_array = np.array(
                [np.double(item.split(" ")) for item in real_xyz_str])
            frac_xyz = self.coord_to_frac(real_xyz_array)
            return frac_xyz

        elements = self.elements
        elm_frac = {elm: get_coords_by_elm(elm) for elm in elements}
        coord_lines = [
            self.format_atom_xyz(item, k) for k, v in elm_frac.items()
            for item in v
        ]
        return coord_lines

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
        vector_strings = self.lattice_vectors
        vector_lines = ["      " + line + "\n" for line in vector_strings]
        lat_block = self.write_block("LATTICE_CART", vector_lines)
        return lat_block

    def block_frac(self) -> List[str]:
        """
        POSITIONS_FRAC block
        returns:
            block: About the atom fractional coords in the lattice. With SPIN if necessary
        """
        lines = self.elm_frac_coords
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
        cellfile = self.castep_dir / f"{stem}.cell"
        contents = [
            self.block_lattice(),
            self.block_frac(),
            self.block_misc(),
            self.block_masses(),
            self.block_pot(),
            self.block_LCAO()
        ]
        text = ''.join((item for block in contents for item in block))
        del contents
        with open(cellfile, 'w', newline='\r\n') as file:
            file.write(text)


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
        cellfile = self.castep_dir / f"{stem}_DOS.cell"
        contents = [
            self.block_lattice(),
            self.block_frac(),
            self.block_misc(),
            self.block_masses(),
            self.block_pot(),
            self.block_LCAO()
        ]
        text = ''.join((item for block in contents for item in block))
        del contents
        with open(cellfile, 'w', newline='\r\n') as file:
            file.write(text)
