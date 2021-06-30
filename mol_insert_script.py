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
    def write_perl(self, lines: List[str], outdir: Path):
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
        text = headlines + array_lines + operations
        with open(outdir / f"{outdir}_insertion.pl", 'w') as output:
            output.writelines(text)

    def output_by_dir(self, lat_dir: Path):
        """
        Output scripts by directory
        """
        outdir = Path(lat_dir.name + f"_{self.mol.filepath.stem}")
        if not outdir.exists():
            outdir.mkdir(parents=True)
        files = [item for item in lat_dir.iterdir() if 'xsd' in item.name]
        files.sort()
        res = p_map(self.adsorbate_setup, files)
        self.write_perl(res, outdir)


def main(use_mol: str, mol_z: float, lat_dir: str):
    """
    Main program to execute
    Args:
        use_mol (str): molecule to be used
        lat_dir (str): lattice file directory pattern
    """
    root = Path.cwd()
    mol_file = Path(f"graphdiyne/molecules_models/{use_mol}.msi")
    dirs = [item for item in root.rglob(lat_dir) if item.is_dir()]
    scriptor = Scriptor(mol_file, mol_z)
    for dir_path in dirs:
        scriptor.output_by_dir(dir_path)
    print("Done")


if __name__ == "__main__":
    Fire(main)
