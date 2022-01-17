"""
Math related helper
"""
import numpy as np


def rotation_matrix(radian_angle: float, axis: str) -> np.ndarray:
    """
    Return rotation matrix by given angle and axis.
    """
    if radian_angle == np.pi/2 or radian_angle== np.pi/2 * 3:
        cos_theta = 0
        sin_theta = np.sin(radian_angle)
    elif radian_angle == np.pi or radian_angle == np.pi *2:
        cos_theta = np.cos(radian_angle)
        sin_theta = 0
    else:
        cos_theta = np.cos(radian_angle)
        sin_theta = np.sin(radian_angle)

    match axis:
        case 'x':
            return np.array([[1, 0, 0], [0, cos_theta, -1 * sin_theta],
                         [0, sin_theta, cos_theta]])
        case 'y':
            return np.array([[cos_theta, 0, sin_theta], [0, 1, 0],
                         [-1 * sin_theta, 0, cos_theta]])
        case 'z':
            return np.array([[cos_theta, -1 * sin_theta, 0],
                         [sin_theta, cos_theta, 0], [0, 0, 1]])
        case _:
            raise ValueError(f"Wrong axis value: {axis}")

def vector_angle(vec_1: np.ndarray, vec_2: np.ndarray)->float:
    """
    Compute angle between two vectors
    """
    assert vec_1.shape == vec_2.shape
    u1 = vec_1/np.linalg.norm(vec_1)
    u2 = vec_2/np.linalg.norm(vec_2)
    angle = np.arccos(np.dot(u1, u2))
    return angle

def rotate_around_center(arr: np.ndarray, radian_angle:float,
                         axis:str)->np.ndarray:
    """
    Perform rotation on a set of coordinates
    """
    r_m = rotation_matrix(radian_angle, axis)
    centroid = arr.mean(axis=0)
    to_origin = arr - centroid
    rotated = np.dot(to_origin, r_m)
    rotated = rotated + centroid
    return rotated
