from multiprocessing import Event, Manager, Process, Queue
from multiprocessing.managers import ValueProxy
import time

from matplotlib.colors import Colormap
import numpy as np
import open3d as o3d

from .process_pcd_ui import PcdUiProcess
from .geometry_provider import GeometryProviderInterface
from .pcd_data_config import PcdDataConfig


class PcdDataProcess:
    def __init__(self, 
                 ui: PcdUiProcess,
                 provider: list[GeometryProviderInterface],
                 config: PcdDataConfig,
                 first_frame: int = 1,
                 debug: bool = False):
        if debug:
            print("DataProcess.__init__")
        self.stream_closed_event = Event()
        self.current_frame = Manager().Value("i", first_frame)
        self.config = config
        self._process = Process(
            target=_data_process_run,
            args=(provider, ui.queue, self.current_frame, debug))

    def start(self):
        self._process.start()

    def request_frame(self, frame_index: int):
        self.current_frame.value = frame_index


def _data_process_run(
        provider_list: list[GeometryProviderInterface],
        ui_queue: Queue,
        current_frame: ValueProxy[int],
        debug: bool):
    previous_frame = -1

    try:
        while True:
            if previous_frame == current_frame.value:
                time.sleep(0.01)
                continue
            previous_frame = current_frame.value

            new_geometries = []
            skipped = False
            for provider in provider_list:
                gs = provider.get_at(current_frame.value)
                if provider.skip_frame_when_empty() and len(gs) == 0:
                    skipped = True
                    break
                if gs is not None:
                    new_geometries.extend(gs)
            if skipped:
                if debug:
                    print("DataProcess: Skipped index", current_frame.value)
                time.sleep(0.01)
                continue

            if debug:
                print("DataProcess: Processing index", current_frame.value)
            ui_queue.put(new_geometries)
    except Exception as e:
        print("DataProcess: Error", e)
    finally:
        if debug:
            print("DataProcess: Finished")
