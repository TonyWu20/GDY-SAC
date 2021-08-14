"""
Substitute metal elements in the base model to generate series of models.
"""
from typing import List
from pathlib import Path
from functools import partial
import xml.etree.ElementTree as ET
import periodictable as pdtable
from p_tqdm import p_map
from fire import Fire


def get_symbols(index_range: range) -> List[str]:
    """
    Get element symbols by atomic numbers
    Args:
        index (list): list of atomic numbers
    returns:
        symbols (list): list of element symbol strings
    """
    symbols = [pdtable.elements[i].symbol for i in index_range]
    return symbols


def mod_element(tree: ET.ElementTree,
                filename: str,
                new_element: str,
                path_folder=None):
    """
    Change the metal element in the GDY SAC base xsd file
    Args:
        tree: Parsed xsd xml tree
        filename: filename, to match the existing metal element in xsd
        new_element: element to be substituted into the xsd file
    returns:
        new_tree: modified xml tree of xsd file
    """
    curr_elm_name = filename.split('_')[-1]
    curr_elm: ET.Element = tree.find(
        f".//Atom3d[@Components='{curr_elm_name}']")
    curr_elm.set('Components', new_element)
    curr_elm.set('Name', new_element)
    output_dest = f"{path_folder}/SAC_GDY_{new_element}.xsd"
    tree.write(output_dest)


def write_models(base_file: Path, element_family: dict):
    """
    Write tree to xsd files
    """
    root = Path.cwd()
    base_tree = ET.parse(base_file)
    filename = base_file.stem
    for key in element_family:
        path_folder = root / f"GDY_SAC_models/{key}"
        if not path_folder.exists():
            path_folder.mkdir(parents=True)
        exec_func = partial(mod_element,
                            base_tree,
                            filename,
                            path_folder=path_folder)
        p_map(exec_func, element_family[key])


def main(base_name: str):
    """
    Main execution
    """
    d3 = get_symbols(range(21, 31))
    d4 = get_symbols(range(39, 49))
    d5 = get_symbols(range(72, 81))
    lm = get_symbols(range(57, 72))
    elements = {'3d': d3, '4d': d4, '5d': d5, 'lm': lm}
    root = Path.cwd()
    base_file = next(root.rglob(base_name))
    write_models(base_file, elements)


if __name__ == "__main__":
    Fire(main)
