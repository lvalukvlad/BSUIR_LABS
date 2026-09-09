import numpy as np

CELL_SIZE = 5

root = None
canvas = None
status_label = None

vertices = []
edges = []

transform_matrix = np.eye(4)

translation = np.array([0.0, 0.0, 0.0])
rotation = np.array([30.0, -25.0, 0.0])
scale = np.array([1.0, 1.0, 1.0])

use_perspective = False
perspective_d = 300.0

object_color = '#0066CC'
edge_color = '#333333'
