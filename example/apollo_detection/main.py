import pandas as pd
import os
import sys

sys.path.append("../../")
import simple_pcd_viewer as spv
from detection_bbox_provider import DetectionBboxProvider

def count_file_num(dir: str) -> int:
    return sum(os.path.isfile(os.path.join(dir, name)) for name in os.listdir(dir))

class FilterInvalid(spv.PcdFilter):
    def filter(self, df: pd.DataFrame) -> bool:
        return True
    
class TransformSample(spv.PcdTransformer):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sample(57600) if len(df) > 57600 else df

target = "benign"

dir = os.path.dirname(__file__).replace("\\", "/")

def get_filename(i):
    return f"{dir}/{target}/{target}_{i:0>4}.pcd"

def get_key(i):
    return f"0405rot/{target}/{target}_{i:0>4}.pcd"
    
def main():
    length = count_file_num(f"{dir}/{target}")
    pcd_provider = spv.PcdFileProvider(
        get_filename=get_filename,
        length=length,
        debug=True
    )
    bbox_provider = DetectionBboxProvider(
        filename=f"{dir}/{target}.txt",
        get_key=get_key,
        length=length,
        debug=True
    )
    ui = spv.PcdUiProcess(debug=True)
    config = spv.PcdDataConfig("pcd", 57600, length, 10.0)
    data_process = spv.PcdDataProcess(
        ui, [pcd_provider, bbox_provider], config, debug=True
    )

    try:
        data_process._process.start()

        controller = spv.TkController(ui, data_process, debug=True)
        controller.show()
    finally:
        ui.close()
        data_process._process.terminate()
        ui.join()

if __name__ == "__main__":
    main()