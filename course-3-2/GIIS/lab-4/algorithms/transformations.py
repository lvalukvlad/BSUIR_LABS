import numpy as np
import math

def create_translation(dx, dy, dz):
    return np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ], dtype=float)

def create_rotation_x(angle):
    c = math.cos(math.radians(angle))
    s = math.sin(math.radians(angle))
    return np.array([
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def create_rotation_y(angle):
    c = math.cos(math.radians(angle))
    s = math.sin(math.radians(angle))
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def create_rotation_z(angle):
    c = math.cos(math.radians(angle))
    s = math.sin(math.radians(angle))
    return np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def create_scaling(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def create_reflection_x():
    return np.array([
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def create_reflection_y():
    return np.array([
        [1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def create_reflection_z():
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def create_perspective(d):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 1/d, 1]
    ], dtype=float)

def multiply_matrices(*matrices):
    result = np.eye(4)
    for m in matrices:
        result = np.dot(result, m)
    return result

def apply_transform(vertex, matrix):
    v = np.array([vertex[0], vertex[1], vertex[2], 1.0])
    result = np.dot(matrix, v)
    if result[3] != 0:
        return (result[0]/result[3], result[1]/result[3], result[2]/result[3])
    return (result[0], result[1], result[2])

def apply_perspective(vertex, d):
    x, y, z = vertex
    if z != 0:
        scale = d / (d - z)
        return (x * scale, y * scale, z)
    return vertex
