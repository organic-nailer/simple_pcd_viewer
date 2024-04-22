from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import pandas as pd
import open3d as o3d
import matplotlib.cm

from .pcd_data_config import PcdDataConfig
from .geometry_provider import GeometryProviderInterface


@abstractmethod
class PcdFilter(ABC):
    @abstractmethod
    def filter(self, df: pd.DataFrame) -> bool:
        pass


@abstractmethod
class PcdTransformer(ABC):
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class CsvDataProvider(GeometryProviderInterface):
    def __init__(
            self,
            dir: str, name: str, length: int,
            filter: Optional[PcdFilter] = None,
            transformer: Optional[PcdTransformer] = None,
            debug: bool = False):
        if debug:
            print("CsvDataProvider.__init__")
        self.debug = debug
        self._dir = dir
        self._name = name
        self._length = length
        self._filter = filter
        self._transformer = transformer
        self.config: PcdDataConfig = PcdDataConfig(name, 57600, length, 10.0)
        self.cmap = matplotlib.cm.get_cmap("viridis")

    def get_at(self, index: int) -> list[o3d.t.geometry.PointCloud]:
        if index >= self._length or index < 0:
            return []
        filename = f"{self._dir}/{self._name}/{self._name}_{index:04d}.csv"
        if self.debug:
            print("CsvDataProvider.get_at:", filename)
        df = pd.read_csv(filename, usecols=["x", "y", "z", "intensity"], dtype={"x": np.float64, "y": np.float64, "z": np.float64, "intensity": int})
        if self._filter is not None and not self._filter.filter(df):
            return []
        if self._transformer is not None:
            df = self._transformer.transform(df)
        
        # pcd = o3d.geometry.PointCloud()
        # pcd.points = o3d.utility.Vector3dVector(df[["x", "y", "z"]].values)
        # pcd.colors = o3d.utility.Vector3dVector(np.zeros((len(df), 3)))
        # return [pcd]

        pcd = o3d.t.geometry.PointCloud()
        pcd.point.positions = o3d.core.Tensor(df[["x", "y", "z"]].values, dtype=o3d.core.Dtype.Float64)
        pcd.point.colors = o3d.core.Tensor(self.cmap(df["intensity"].values / 255)[:, :3], dtype=o3d.core.Dtype.Float32)
        return [pcd]
    
    def skip_frame_when_empty(self) -> bool:
        return True
