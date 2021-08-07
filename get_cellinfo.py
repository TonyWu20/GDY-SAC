"""
Get necessary element informations from .cell file and tabulate
"""
import re
from pathlib import Path
from mendeleev import element
import yaml as y
from fire import Fire


class CellFile:
    """
    Object of Metal + SAC .cell file
    """
    def __init__(self, filepath: Path):
        self.file = filepath
        self.text = filepath.read_text()
        self.metal = filepath.stem.split("_")[2]

    @property
    def spin(self) -> int:
        """
        Metal spin value
        """
        metal_line_re = re.compile(f"{self.metal}.*")
        matched_line = metal_line_re.search(self.text).group(0)
        if not "SPIN" in matched_line:
            spin = 0
        else:
            spin_re = re.compile("SPIN=  ([0-9.]+)")
            spin = int(float(spin_re.search(matched_line).group(1)))
        return spin

    @property
    def mass(self) -> float:
        """
        Metal mass value
        """
        metal_mass_re = re.compile(
            f"%BLOCK SPECIES_MASS\n.*\n.*{self.metal}\s+([0-9.]+)",
            re.MULTILINE)
        mass = float(metal_mass_re.search(self.text).group(1))
        return mass

    @property
    def pot_file(self) -> str:
        """
        Metal potential filename
        """
        pot_re = re.compile(f".*POT\n.*\n.*{self.metal}\s+([A-Za-z0-9._]+)",
                            re.MULTILINE)
        pot_file = pot_re.search(self.text).group(1)
        return pot_file

    @property
    def LCAO(self) -> int:
        """
        Metal LCAO value
        """
        lcao_re = re.compile(f".*LCAO.*\n.*\n.*{self.metal}\s+([0-9]+)",
                             re.MULTILINE)
        lcao_state = int(lcao_re.search(self.text).group(1))
        return lcao_state

    def output_res(self) -> dict:
        """
        Create output dict
        """
        res = {
            self.metal: {
                "spin": self.spin,
                "mass": self.mass,
                "pot": self.pot_file,
                "LCAO": self.LCAO
            }
        }
        return res


def main(dir_name: str):
    """
    Update element_table
    """
    cell_files = list(Path(dir_name).rglob("*.cell"))
    if cell_files == []:
        print("Wrong input dir")
        return
    cell_files = [item for item in cell_files if not "DOS" in item.stem]
    cell_files = sorted(
        cell_files,
        key=lambda x: element(x.stem.split("_")[2]).  #type:ignore
        atomic_number)
    output_dicts = [CellFile(item).output_res() for item in cell_files]
    out_dict = {}
    for item in output_dicts:
        out_dict.update(item)
    res = {"3d": out_dict}
    with open("castep_input/element_table.yaml", 'r') as file:
        table = y.full_load(file)
    table.update(res)
    with open("castep_input/element_table_updated.yaml", 'w') as file:
        y.dump(table, file)


if __name__ == "__main__":
    Fire(main)
