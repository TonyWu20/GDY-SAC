"""
Prepare molecule insertion information to write MS perl script
"""
import re
from pathlib import Path
from typing import List
from functools import partial
from p_tqdm import p_map
from fire import Fire
from graphdiyne import ConfCal as conf


class Scriptor(conf.ModelFactory):
    """
    Write perl script for adsorbate insertion
    """
    def write_perl(self, lines: List[str], outdir: str):
        """
        Write the perl script to use
        Args:
            lines: List of formatted lines
        """
        with open("perl_repo/MS_head.pl", 'r') as file:
            headlines = file.readlines()
        array_lines = ['my @params = (\n'] + lines + [');\n']
        adsorbate = self.mol.filepath.stem
        with open(f"perl_repo/{adsorbate}_insert.pl", 'r') as file:
            operations = file.readlines()
        outdir_re = re.compile(r'(?<=Export\(")([0-9A-Za-z_]+)')
        outdir_line = operations[-4]
        operations[-4] = outdir_re.sub(outdir, outdir_line)
        text = headlines + array_lines + operations
        with open(f"{adsorbate}_insertion.pl", 'w') as output:
            output.writelines(text)


def main(use_mol: str, mol_z: float, lat_pattern: str):
    """
    Main program to execute
    Args:
        use_mol (str): molecule to be used
        pattern (str): pattern to match msi or xsd files
    """
    root = Path.cwd()
    mol_file = Path(f"graphdiyne/molecules_models/{use_mol}.msi")
    files = list(root.rglob(lat_pattern))
    files.sort()
    scriptor = Scriptor(mol_file)
    lat_dir_name = files[0].parent.name
    outdir_name = lat_dir_name + f"_{use_mol}"
    fixed_func = partial(scriptor.adsorbate_setup, mol_height=mol_z)
    res = p_map(fixed_func, files)
    scriptor.write_perl(res, outdir_name)


if __name__ == "__main__":
    Fire(main)
