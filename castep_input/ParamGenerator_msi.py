"""
Generate .param file
"""
import re
from pathlib import Path
import shutil
import dpath.util as dp
from graphdiyne.msi_lattice import MsiLattice


class ParamFile(MsiLattice):
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
        fine_energy = re.compile(r"([0-9]+)\s+FINE")
        try:
            cutoff_vals = [
                int(fine_energy.search(item.read_text()).group(1))
                for item in pot_files
            ]
        except AttributeError:
            print(self.metal)

        def roundup_tenth(number: float):
            """
            Round up number to the bigger nearest tenth.
            E.g.: 374 -> 380; 376 -> 380.
            Args:
                number (float)
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
        param_file = self.castep_dir / f"{stem}.param"
        return param_file

    @property
    def dos_param_filename(self):
        """
        Output filename for .param
        """
        stem = self.filepath.stem
        param_file = self.castep_dir / f"{stem}_DOS.param"
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

    def copy_potentials(self):
        """
        Copy specified potentials to directory
        """
        potentials = self.get_potentials()
        new_dest = [self.castep_dir / f"{file.name}" for file in potentials]
        for source, dest in zip(potentials, new_dest):
            shutil.copy(source, dest)

    def write_pbs_scripts(self):
        """
        Generate hpc.pbs.sh for server running
        """
        seed_name = self.filepath.stem
        cmd_prefix = "mpirun --mca btl ^tcp --hostfile hostfile /home/bhuang/castep.mpi"
        cmd = f"{cmd_prefix} {seed_name}\n"
        eof = "rm ./hostfile"
        template = Path("castep_input/pbs_template.sh")
        contents = template.read_text() + cmd + eof
        with open(self.castep_dir / "hpc.pbs.sh", 'w', newline='\r\n') as file:
            file.write(contents)


class MiscFile(MsiLattice):
    """
    Misc files generations.
    """
    def write_kptaux(self):
        """
        Generate .kptaux file
        """
        content = ("MP_GRID :        1       1       1\n"
                   "MP_OFFSET :   0.000000000000000e+000"
                   " 0.000000000000000e+000"
                   " 0.000000000000000e+000\n"
                   "%BLOCK KPOINT_IMAGES\n"
                   "   1   1\n"
                   "%ENDBLOCK KPOINT_IMAGES")
        filepath = self.castep_dir / f"{self.filepath.stem}.kptaux"
        dos_filepath = self.castep_dir / f"{self.filepath.stem}_DOS.kptaux"
        with open(filepath, 'w', newline='\r\n') as file:
            file.write(content)
        with open(dos_filepath, 'w', newline='\r\n') as file:
            file.write(content)

    def write_trjaux(self):
        """
        Generate .trjaux file
        """
        atom_ids = self.atom_ids_by_elm
        start_comments = ("# Atom IDs to appear in any .trj file to be"
                          " generated.\n"
                          "# Correspond to atom IDs which will be used"
                          " in exported .msi file\n"
                          "# required for animation/analysis of trajectory"
                          " within Cerius2.\n")
        atom_ids_lines = [f"{item}\n" for item in atom_ids]
        end_comments = ("#Origin  0.000000000000000e+000 "
                        "0.000000000000000e+000  0.000000000000000e+000")
        contents = [start_comments] + atom_ids_lines + [end_comments]
        filepath = self.castep_dir / f"{self.filepath.stem}.trjaux"
        with open(filepath, 'w', newline='\r\n') as file:
            file.writelines(contents)

    def copy_smcastep(self):
        """
        Copy SMCastep_Extension
        """
        extension = Path("castep_input/SMCastep_Extension.xms")
        new_dest = self.castep_dir / f"SMCastep_Extension_{self.filepath.stem}.xms"
        shutil.copy(extension, new_dest)

    def move_structures(self):
        """
        Move structure files into castep folder
        """
        msi_file = self.filepath
        new_dest = self.castep_dir / msi_file.name
        msi_file.rename(new_dest)
        xsd_file = self.filepath.parent / f"{self.filepath.stem}.xsd"
        new_xsd_dest = self.castep_dir / xsd_file.name
        xsd_file.rename(new_xsd_dest)
