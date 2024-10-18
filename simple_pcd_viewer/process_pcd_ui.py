from multiprocessing import Process, Event, Queue, Manager
from multiprocessing.synchronize import Event as EventClass
import numpy as np
import open3d as o3d

class PcdUiProcess:
    def __init__(self, max_points_num: int = 57600, debug: bool = False):
        self.queue = Queue()
        self._finished = False
        self.current_status = Manager().dict()
        self.event = Event()
        self.stream_close_event = Event()
        self.window_close_event = Event()

        self._process = Process(target=_pcd_ui_process_run, args=(
            self.queue,
            self.current_status,
            max_points_num,
            self.stream_close_event,
            self.window_close_event,
            debug))
        self._process.start()

    def close(self):
        self.stream_close_event.set()

    def join(self):
        self._process.join()


def _pcd_ui_process_run(
        queue: Queue,
        status: dict,
        max_points_num: int,
        stream_close_event: EventClass,
        window_close_event: EventClass,
        debug: bool):
    if debug:
        print("PcdUiProcess._pcd_ui_process_run")
    points = np.zeros((max_points_num, 3))
    colors = np.zeros((max_points_num, 3))
    vis = o3d.visualization.Visualizer()  # type: ignore
    vis.create_window(window_name="Simple PCD Viewer")
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    vis.add_geometry(pcd)

    render_option = vis.get_render_option()
    render_option.background_color = np.asarray([0.13, 0.13, 0.13])

    grid = _get_grid()
    for g in grid:
        vis.add_geometry(g)

    # start = time.time()
    # frame_max = 10
    # frame_num = 0

    is_first = True
    prev_geometries = []

    try:
        while (not stream_close_event.is_set()) or (not queue.empty()):
            render_option = vis.get_render_option()
            view_control = vis.get_view_control()
            pinhole_params = view_control.convert_to_pinhole_camera_parameters()
            status["point_size"] = render_option.point_size
            status["line_width"] = render_option.line_width
            status["background_color"] = render_option.background_color
            status["intrinsics"] = pinhole_params.intrinsic.intrinsic_matrix
            status["extrinsics"] = pinhole_params.extrinsic
            status["fov"] = view_control.get_field_of_view()
            if not queue.empty():
                # s = time.time()
                while not queue.empty():
                    geometries = queue.get()
                # print(f"Get Time: {time.time() - s:.5f}")
                # s = time.time()
                for g in prev_geometries:
                    vis.remove_geometry(g, reset_bounding_box=False)
                prev_geometries.clear()

                for g in geometries:
                    g = g.to_legacy()
                    vis.add_geometry(g, reset_bounding_box=False)
                    prev_geometries.append(g)


                if is_first:
                    vis.reset_view_point(True)
                    is_first = False
                # print(f"Transform Time: {time.time() - s:.5f}")
                # vis.update_geometry(pcd)
                # frame_num += 1
                # if frame_num == frame_max:
                #     print(f"FPS: {frame_max / (time.time() - start):.2f}")
                #     start = time.time()
                #     frame_num = 0
            if not vis.poll_events():
                break
            vis.update_renderer()
    except Exception as e:
        print("PcdUiProcess: Error", e)
    finally:
        while not queue.empty():
            queue.get()
        queue.close()
        window_close_event.set()
        vis.destroy_window()
        if debug:
            print("PcdUiProcess Finished")


def _gen_grid(pitch: float, length: int) -> o3d.geometry.LineSet:
    line_set = o3d.geometry.LineSet()
    max_value = length * pitch
    x = np.arange(-max_value, max_value+pitch, pitch)
    x = np.repeat(x, 2)
    y = np.full_like(x, -max_value)
    y[::2] = max_value
    z = np.zeros_like(x)
    points_Y = np.vstack((x, y, z)).T

    y = np.arange(-max_value, max_value+pitch, pitch)
    y = np.repeat(y, 2)
    x = np.full_like(y, -max_value)
    x[::2] = max_value
    z = np.zeros_like(y)
    points_X = np.vstack((x, y, z)).T

    points = np.vstack((points_X, points_Y))
    line_set.points = o3d.utility.Vector3dVector(points)
    lines = np.arange(points.shape[0]).reshape(-1, 2)
    line_set.lines = o3d.utility.Vector2iVector(lines)

    line_set.paint_uniform_color((0.3, 0.3, 0.3))

    return line_set


def _gen_circle(r: float, point_num: int = 100) -> o3d.geometry.LineSet:
    theta = np.linspace(0, 2*np.pi, point_num)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.zeros_like(x)

    points = np.vstack((x, y, z)).T
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(points)
    lines = np.zeros((points.shape[0]-1, 2), dtype=int)
    lines[:, 0] = np.arange(points.shape[0]-1)
    lines[:, 1] = np.arange(points.shape[0]-1) + 1
    line_set.lines = o3d.utility.Vector2iVector(lines)

    line_set.paint_uniform_color((0.3, 0.3, 0.3))

    return line_set


def _get_grid() -> list[o3d.geometry.LineSet]:
    return [
        _gen_grid(10, 10),
        _gen_circle(10),
        _gen_circle(20),
        _gen_circle(30),
        _gen_circle(40),
        _gen_circle(50),
        _gen_circle(60),
        _gen_circle(70),
        _gen_circle(80),
        _gen_circle(90),
        _gen_circle(100),
    ]
