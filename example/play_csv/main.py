import os
import sys
import pandas as pd

sys.path.append("../../")
import simple_pcd_viewer as spv


class FilterInvalid(spv.PcdFilter):
    def filter(self, df: pd.DataFrame) -> bool:
        return len(df) > 1000


class TransformSample(spv.PcdTransformer):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sample(57600) if len(df) > 57600 else df

def count_file_num(dir: str) -> int:
    return sum(os.path.isfile(os.path.join(dir, name)) for name in os.listdir(dir))

def main():
    dir = os.path.dirname(__file__).replace("\\", "/")
    target = "A"
    length = count_file_num(f"{dir}/{target}")
    vis = spv.CsvVisualizer(
        dir, target, length,
        FilterInvalid(),
        TransformSample(),
        debug=True)
    vis.show()


if __name__ == "__main__":
    main()
