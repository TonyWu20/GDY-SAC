"""
Math related helper
"""
import numpy as np


def rotation_matrix(radian_angle: float, axis: str) -> np.ndarray:
    """
    Return rotation matrix by given angle and axis.
    """
    if (round(np.degrees(radian_angle)) % 90
            == 0) and (np.degrees(radian_angle) % 180 != 0):
        cos_theta = 0
        sin_theta = np.sin(radian_angle)
    elif round(np.degrees(radian_angle)) % 180 == 0:
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
