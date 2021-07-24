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
    def write_perl(self, lines: List[str], outdir: Path, site: str):
        """
        Write the perl script to use
        Args:
            lines: List of formatted lines
        """
        headlines = [
            '#!perl\n', 'use strict;\n', 'use Getopt::Long;\n',
            'use MaterialsScript qw(:all);\n'
        ]
        array_lines = ['my @params = (\n'] + lines + [');\n']
        operations = self.build_actions(site)
        text = headlines + array_lines + operations
        with open(f"{outdir}/generate_model.pl", 'w') as output:
            output.writelines(text)

    def generate_scripts(self, lat_dir: Path, site: str):
        """
        Output scripts by directory
        """
        outdir = Path(lat_dir.name + f"_{self.mol.filepath.stem}/{site}")
        if not outdir.exists():
            outdir.mkdir(parents=True)
        files = [item for item in lat_dir.iterdir() if 'xsd' in item.name]
        files.sort()
        setup = partial(self.adsorbate_setup, site=site)
        res = p_map(setup, files)
        self.write_perl(res, outdir, site)


def main(use_mol: str, lat_dir: str, mol_z: float = 1.54221):
    """
    Main program to execute
    Args:
        use_mol (str): molecule to be used
        lat_dir (str): lattice file directory pattern
    """
    root = Path.cwd()
    mol_file = Path(f"graphdiyne/molecules_models/{use_mol}.msi")
    dirs = [item for item in root.rglob(lat_dir) if item.is_dir()]
    sites = ['metal', 'c1', 'c2', 'c3', 'c4', 'c5']
    scriptor = Scriptor(mol_file, mol_z)
    for dir_path in dirs:
        for site in sites:
            scriptor.generate_scripts(dir_path, site)
    print("Done")


if __name__ == "__main__":
    Fire(main)
