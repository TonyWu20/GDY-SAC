"""
Generate .param file
"""
import re
from pathlib import Path
import dpath.util as dp
from castep_input.CellGenerator import GDYLattice


class ParamFile(GDYLattice):
    """
    Class of .param file
    """
    def get_potentials(self):
        """
        get elements' potential files
        """
        elements = self.elements
        potentials = [dp.get(self.table, f"*/{elm}/pot") for elm in elements]
        pot_files = [
            next(Path("castep_input/Potentials/").rglob(pot))
            for pot in potentials
        ]
        return pot_files

    @property
    def cutoff_energy(self) -> str:
        """
        Determine cutoff energy from pseudopotential files. Quality: Ultrafine
        (1.1 times of FINE)
        """
        pot_files = self.get_potentials()
        fine_energy = re.compile(r"([0-9]+) FINE")
        cutoff_vals = [
            int(fine_energy.search(item.read_text()).group(1))
            for item in pot_files
        ]

        def roundup_tenth(number: int):
            """
            Round up number to the bigger nearest tenth.
            E.g.: 374 -> 380; 376 -> 380.
            Args:
                number (int)
            returns:
                res (int): bigger nearest tenth.
            """
            rem = number % 10
            if rem < 5:
                res = round(number / 10) * 10 + 10
            else:
                res = round(number, -1)  #type: ignore
            return int(res)

        fine_cutoff = [roundup_tenth(1.1 * num) for num in cutoff_vals]
        final_cutoff = str(max(fine_cutoff))
        return final_cutoff

    @property
    def param_filename(self):
        """
        Output filename for .param
        """
        stem = self.filepath.stem
        param_file = self.filepath.parent / f"{stem}_test.param"
        return param_file

    @property
    def dos_param_filename(self):
        """
        Output filename for .param
        """
        stem = self.filepath.stem
        param_file = self.filepath.parent / f"{stem}_DOS_test.param"
        return param_file

    def write_param(self):
        """
        Generate param file by modifying key parameters.
        """
        geom_param = Path("castep_input/geom.param")
        text = geom_param.read_text()
        cutoff_pat = re.compile(r"(?<=cut_off_energy :\s{6})([0-9]+)")
        spin_pat = re.compile(r"(?<=spin :\s{8})([0-9]+)")
        sub_cutoff = cutoff_pat.sub(self.cutoff_energy, text)
        sub_spin = spin_pat.sub(str(self.spin), sub_cutoff)
        with open(self.param_filename, 'w', newline='\r\n') as file:
            file.write(sub_spin)

    def write_dos_param(self):
        """
        Generate dos_param file by modifying key parameters.
        """
        dos_param = Path("castep_input/dos.param")
        text = dos_param.read_text()
        cutoff_pat = re.compile(r"(?<=cut_off_energy :\s{6})([0-9]+)")
        spin_pat = re.compile(r"(?<=spin :\s{8})([0-9]+)")
        sub_cutoff = cutoff_pat.sub(self.cutoff_energy, text)
        sub_spin = spin_pat.sub(str(self.spin), sub_cutoff)
        with open(self.dos_param_filename, 'w', newline='\r\n') as file:
            file.write(sub_spin)
