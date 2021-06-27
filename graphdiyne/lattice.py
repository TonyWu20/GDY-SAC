"""
Python scripts to parse GDY SAC lattice model in xsd format
"""
from typing import Tuple
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np


class GDYLattice:
    """
    Object of gdy lattice
    """
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.tree = ET.parse(self.filepath)
        self.metal = filepath.stem.split("_")[-1]

    @property
    def lat_param(self) -> Tuple[np.float64]:
        """
        lattice parameter in xsd file
        """
        lat_info = self.tree.find('.//SpaceGroup')
        str_a, str_b, str_c = (
            lat_info.get(key)  #type:ignore
            for key in ['AVector', 'BVector', 'CVector'])

        def str_to_array(vec_str: str) -> np.ndarray:
            """
            convert the vector string to array
            Args:
                vec_str: string of vector
            returns:
                arr : vector in array form
            """
            values = vec_str.split(',')
            arr = np.array([float(item) for item in values])
            return arr

        vectors = (
            str_to_array(item)  #type:ignore
            for item in [str_a, str_b, str_c])
        lat_params = tuple(np.linalg.norm(vec) for vec in vectors)
        return lat_params  #type: ignore

    @property
    def metal_xyz(self) -> np.ndarray:
        """
        Get metal xyz coordinates
        """
        metal = self.tree.find(f'.//Atom3d[@Name="{self.metal}"]')
        xyz_str = metal.get('XYZ')  #type: ignore
        xyz_array = np.array([float(item)
                              for item in xyz_str.split(',')])  #type: ignore
        return xyz_array
