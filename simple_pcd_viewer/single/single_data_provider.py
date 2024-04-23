from typing import Union, Optional
from enum import Enum
import numpy as np
import pandas as pd
import open3d as o3d
from matplotlib.colors import Colormap
import matplotlib

from simple_pcd_viewer.geometry_provider import GeometryProviderInterface

DataType = Union[
    np.ndarray, 
    str, 
    pd.DataFrame, 
    o3d.geometry.PointCloud, 
    o3d.t.geometry.PointCloud
]

class ColorizeType(Enum):
    NONE = 0
    CMAP = 1
    RGB = 2

class PcdReadingRule:
    def __init__(self,
                 x_key: str = "x",
                 y_key: str = "y",
                 z_key: str = "z",
                 x_index: int = 0,
                 y_index: int = 1,
                 z_index: int = 2,
                 colorize_type: ColorizeType = ColorizeType.CMAP,
                 colorize_rgb_indices: list[int] = [3, 4, 5],
                 colorize_key: Optional[str] = "intensity",
                 colorize_index: int = 3,
                 colorize_min: float = 0.0,
                 colorize_max: float = 255.0,
                 colormap: Optional[Colormap] = None) -> None:
        self.x_key = x_key
        self.y_key = y_key
        self.z_key = z_key
        self.x_index = x_index
        self.y_index = y_index
        self.z_index = z_index
        self.colorize_type = colorize_type
        self.colorize_rgb_indices = colorize_rgb_indices
        self.colorize_key = colorize_key
        self.colorize_index = colorize_index
        self.colorize_min = colorize_min
        self.colorize_max = colorize_max
        self.colormap = colormap if colormap is not None else matplotlib.colormaps["viridis"]

class SingleDataProvider(GeometryProviderInterface):
    def __init__(self, 
                 data: DataType,
                 rule: PcdReadingRule,
                 debug: bool = False) -> None:
        if debug:
            print("SingleDataProvider.__init__")
        self.debug = debug
        self.data = data
        self.rule = rule

    def get_at(self, index: int) -> list[o3d.t.geometry.PointCloud]:
        if index != 0:
            return []
        return [data2pcd(self.data, self.rule)]
    
    def skip_frame_when_empty(self) -> bool:
        return False


def data2pcd(data: DataType, rule: PcdReadingRule) -> o3d.t.geometry.PointCloud:
    if isinstance(data, np.ndarray):
        return _data2pcd_numpy_array(data, rule)
    elif isinstance(data, str):
        return _data2pcd_filename(data, rule)
    elif isinstance(data, pd.DataFrame):
        return _data2pcd_dataframe(data, rule)
    elif isinstance(data, o3d.geometry.PointCloud):
        return o3d.t.geometry.PointCloud.from_legacy(data)
    elif isinstance(data, o3d.t.geometry.PointCloud):
        return data
    else:
        raise ValueError("Unsupported data type")
    
def _data2pcd_numpy_array(data: np.ndarray, rule: PcdReadingRule) -> o3d.t.geometry.PointCloud:
    pcd = o3d.t.geometry.PointCloud()
    xyz = data[:, [rule.x_index, rule.y_index, rule.z_index]]
    pcd.point.positions = o3d.core.Tensor(xyz, dtype=o3d.core.Dtype.Float64)
    if rule.colorize_type == ColorizeType.CMAP:
        normed_value = (data[:, rule.colorize_index] - rule.colorize_min) / (rule.colorize_max - rule.colorize_min)
        colors = rule.colormap(normed_value)[:, :3]
        pcd.point.colors = o3d.core.Tensor(colors, dtype=o3d.core.Dtype.Float32)
    elif rule.colorize_type == ColorizeType.RGB:
        colors = data[:, rule.colorize_rgb_indices]
        pcd.point.colors = o3d.core.Tensor(colors, dtype=o3d.core.Dtype.Float32)
    return pcd

def _data2pcd_filename(filename: str, rule: PcdReadingRule) -> o3d.t.geometry.PointCloud:
    ext = filename.split(".")[-1]
    if ext == "csv":
        df = pd.read_csv(filename, usecols=[rule.x_key, rule.y_key, rule.z_key, rule.colorize_key])
        return _data2pcd_dataframe(df, rule)
    elif ext == "pcd":
        pcd = o3d.t.io.read_point_cloud(filename)
        return pcd
    else:
        raise ValueError("Unsupported file extension: " + ext)
    
def _data2pcd_dataframe(df: pd.DataFrame, rule: PcdReadingRule) -> o3d.t.geometry.PointCloud:
    pcd = o3d.t.geometry.PointCloud()
    pcd.point.positions = o3d.core.Tensor(df[[rule.x_key, rule.y_key, rule.z_key]].values, dtype=o3d.core.Dtype.Float64)
    if rule.colorize_type == ColorizeType.CMAP:
        normed_value = np.array((df[rule.colorize_key] - rule.colorize_min) / (rule.colorize_max - rule.colorize_min))
        colors = rule.colormap(normed_value)[:, :3]
        pcd.point.colors = o3d.core.Tensor(colors, dtype=o3d.core.Dtype.Float32)
    elif rule.colorize_type == ColorizeType.RGB:
        colors = df.iloc[:, rule.colorize_rgb_indices].values
        pcd.point.colors = o3d.core.Tensor(colors, dtype=o3d.core.Dtype.Float32)
    return pcd
