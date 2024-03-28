import pandas as pd
import simple_pcd_viewer as spv


class FilterInvalid(spv.PcdFilter):
    def filter(self, df: pd.DataFrame) -> bool:
        return len(df) > 1000


class TransformSample(spv.PcdTransformer):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sample(57600) if len(df) > 57600 else df


def main():
    vis = spv.CsvVisualizer(
        ".", "0315", 290,
        FilterInvalid(),
        TransformSample(),
        debug=True)
    vis.show()


if __name__ == "__main__":
    main()
