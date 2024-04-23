import sys
import os

sys.path.append("../../")
import simple_pcd_viewer as spv
import pandas as pd

filename = os.path.dirname(__file__).replace("\\", "/") + "/data.csv"

def main():
    df = pd.read_csv(filename)
    df = df.query("distance_m < 20.0")
    vis = spv.single.SingleFrameVisualizer(df, debug=True)
    vis.show()

if __name__ == "__main__":
    main()
