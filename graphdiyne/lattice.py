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
    def lat_vectors(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        lattice vectors in xsd file
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

        vec_a, vec_b, vec_c = (
            str_to_array(item)  #type:ignore
            for item in [str_a, str_b, str_c])
        return (vec_a, vec_b, vec_c)

    @property
    def lat_params(self) -> Tuple[np.float64]:
        """
        Get lattice params
        """
        vectors = self.lat_vectors
        lat_params = tuple(np.linalg.norm(vec) for vec in vectors)
        return lat_params  #type: ignore

    @property
    def lattice_angle(self) -> tuple:
        """
        Determine lattice angle: alpha, beta, gamma
        """
        vec_a, vec_b, vec_c = self.lat_vectors
        alpha = np.arccos(
            np.clip(
                np.dot(vec_b / np.linalg.norm(vec_b),
                       vec_c / np.linalg.norm(vec_c)), -1, 1))
        beta = np.arccos(
            np.clip(
                np.dot(vec_a / np.linalg.norm(vec_a),
                       vec_c / np.linalg.norm(vec_c)), -1, 1))
        gamma = np.arccos(
            np.clip(
                np.dot(vec_a / np.linalg.norm(vec_a),
                       vec_b / np.linalg.norm(vec_b)), -1, 1))
        return (alpha, beta, gamma)

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

    @property
    def rotation_vector(self):
        """
        Determine x or y to align with when putting molecules
        """
        theta = np.pi / 3
        cos, sin = np.cos(theta), np.sin(theta)
        rot_matrix = np.array([[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]])
        return rot_matrix

    def convert_xyz(self, mol_coordinates: np.ndarray):
        """
        Convert external molecule real xyz coordinates into fractional xyz
        Args:
            mol_coordinates: array of xyz coordinates
        """
        a, b, c = self.lat_params
        vec_a, vec_b, vec_c = self.lat_vectors
        V = np.dot(vec_a, np.cross(vec_b, vec_c))
        cos_y = np.cos(np.pi * 2 / 3)
        sin_y = np.sin(np.pi * 2 / 3)
        M = np.array([[-1 * cos_y / (a * sin_y), 1 / a, 0],
                      [1 / (b * sin_y), 0, 0], [0, 0, a * b * sin_y / V]])
        new_coordinates = np.dot(mol_coordinates, M)
        return new_coordinates
