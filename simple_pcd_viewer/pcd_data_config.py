class PcdDataConfig:
    def __init__(self,
                 name: str,
                 max_points_num: int,
                 frame_num: int,
                 fps: float,):
        self.name = name
        self.max_points_num = max_points_num
        self.frame_num = frame_num
        self.fps = fps
