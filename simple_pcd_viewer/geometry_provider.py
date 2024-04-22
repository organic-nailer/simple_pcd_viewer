from abc import ABC, abstractmethod

import open3d as o3d

class GeometryProviderInterface(ABC):
    @abstractmethod
    def get_at(self, index: int) -> list[o3d.geometry.Geometry]:
        pass

    @abstractmethod
    def skip_frame_when_empty(self) -> bool:
        pass
