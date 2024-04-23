from typing import Optional
from collections.abc import Callable

import open3d as o3d
import numpy as np
import sys
sys.path.append("../../")
import simple_pcd_viewer as spv
from parse_detection import parse_file_to_dict, DetectedObject

class DetectionBboxProvider(spv.GeometryProviderInterface):
    def __init__(
            self,
            filename: str,
            get_key: Callable[[int], str],
            length: int,
            debug: bool = False):
        if debug:
            print("DetectionBboxProvider.__init__")
        self.debug = debug
        self._filename = filename
        self._get_key = get_key
        self._length = length
        self.obj_dict = parse_file_to_dict(filename)

    def get_at(self, index: int) -> list[o3d.geometry.LineSet]:
        if index >= self._length or index < 0:
            return []
        key = self._get_key(index)
        obj_list = self.obj_dict[key]
        if self.debug:
            print("DetectionBboxProvider.get_at:", key)
        return [obj_to_line_set(obj) for obj in obj_list]
    
    def skip_frame_when_empty(self) -> bool:
        return False

def calc_color(label: int, score: float) -> np.ndarray:
    if label in [0, 1, 2, 3, 4]:
        return np.array([min(1.0, score * 2.0), 0, 0])
    elif label in [7]:
        return np.array([0, 1.0, 0])
    elif label in [5,6]:
        return np.array([0, 0, min(1.0, score * 2.0)])
    else:
        return np.array([min(1.0, score * 2.0), min(1.0, score * 2.0), min(1.0, score * 2.0)])

def obj_to_line_set(obj: DetectedObject) -> o3d.geometry.LineSet:
    x = obj.x
    y = obj.y
    z = obj.z
    dx = obj.dx
    dy = obj.dy
    dz = obj.dz
    points = np.array([
        [x - dx / 2, y - dy / 2, z - dz / 2],
        [x - dx / 2, y - dy / 2, z + dz / 2],
        [x - dx / 2, y + dy / 2, z - dz / 2],
        [x - dx / 2, y + dy / 2, z + dz / 2],
        [x + dx / 2, y - dy / 2, z - dz / 2],
        [x + dx / 2, y - dy / 2, z + dz / 2],
        [x + dx / 2, y + dy / 2, z - dz / 2],
        [x + dx / 2, y + dy / 2, z + dz / 2],
    ])
    lines = np.array([
        [0, 1], [0, 2], [0, 4],
        [1, 3], [1, 5],
        [2, 3], [2, 6],
        [3, 7],
        [4, 5], [4, 6],
        [5, 7],
        [6, 7],
    ])
    device = o3d.core.Device("CPU:0")
    lineset = o3d.t.geometry.LineSet()
    lineset.point.positions = o3d.core.Tensor(points, o3d.core.float32, device)
    lineset.line.indices = o3d.core.Tensor(lines, o3d.core.int32, device)

    color = calc_color(obj.label, obj.score)
    lineset.line.colors = o3d.core.Tensor(np.tile(color, (len(lines), 1)), o3d.core.float32, device)

    R = o3d.geometry.get_rotation_matrix_from_xyz([0, 0, obj.yaw])
    lineset.rotate(R, center=[x, y, z])
    return lineset