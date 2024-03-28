from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import pandas as pd

from simple_pcd_viewer.pcd_data_config import PcdDataConfig


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


class CsvDataProvider:
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

    def get_at(self, index: int) -> Optional[pd.DataFrame]:
        if index >= self._length or index < 0:
            return None
        filename = f"{self._dir}/{self._name}/{self._name}_{index:04d}.csv"
        if self.debug:
            print("CsvDataProvider.get_at:", filename)
        df = pd.read_csv(filename, usecols=["x", "y", "z", "intensity"], dtype={"x": np.float64, "y": np.float64, "z": np.float64, "intensity": int})
        if self._filter is not None and not self._filter.filter(df):
            return None
        if self._transformer is not None:
            df = self._transformer.transform(df)
        return df
