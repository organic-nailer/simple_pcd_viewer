import sys
import os

sys.path.append("../../")
import simple_pcd_viewer as spv
import numpy as np

def main():
    points = np.random.rand(100, 3) * 10 - 5
    colors = np.random.rand(100, 3)

    rule = spv.single.PcdReadingRule(colorize_type=spv.single.ColorizeType.RGB)
    vis = spv.single.SingleFrameVisualizer(np.hstack([points,colors]), rule=rule, debug=True)
    vis.show()

if __name__ == "__main__":
    main()
