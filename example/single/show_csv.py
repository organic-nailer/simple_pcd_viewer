import sys
import os

sys.path.append("../../")
import simple_pcd_viewer as spv

filename = os.path.dirname(__file__).replace("\\", "/") + "/data.csv"

def main():
    vis = spv.single.SingleFrameVisualizer(filename, debug=True)
    vis.show()

if __name__ == "__main__":
    main()
