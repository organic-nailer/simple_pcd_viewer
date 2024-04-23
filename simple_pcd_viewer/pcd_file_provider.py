from typing import Optional
from collections.abc import Callable

import open3d as o3d
from .pcd_data_config import PcdDataConfig
from .geometry_provider import GeometryProviderInterface

class PcdFileProvider(GeometryProviderInterface):
    def __init__(
            self,
            get_filename: Callable[[int], str],
            length: int,
            debug: bool = False):
        if debug:
            print("PcdFileProvider.__init__")
        self.debug = debug
        self._get_filename = get_filename
        self._length = length
        self.config = PcdDataConfig("pcd", 57600, length, 10.0)

    def get_at(self, index: int) -> list[o3d.geometry.PointCloud]:
        if index >= self._length or index < 0:
            return []
        filename = self._get_filename(index)
        if self.debug:
            print("PcdFileProvider.get_at:", filename)
        pcd = o3d.t.io.read_point_cloud(filename)
        pcd.paint_uniform_color([0.5, 0.5, 0.5])
        return [pcd]
    
    def skip_frame_when_empty(self) -> bool:
        return False
