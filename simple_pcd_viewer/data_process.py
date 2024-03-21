from multiprocessing import Event, Manager, Process, Queue
from multiprocessing.managers import ValueProxy
import time

from matplotlib.colors import Colormap
import numpy as np

from simple_pcd_viewer.csv_data_provider import CsvDataProvider
from simple_pcd_viewer.window import PcdUiProcess


class DataProcess:
    def __init__(self, ui: PcdUiProcess, provider: CsvDataProvider, cmap: Colormap):
        self.stream_closed_event = Event()
        self.current_frame = Manager().Value("i", 0)
        self.config = provider.config
        self._process = Process(
            target=_data_process_run,
            args=(provider, ui.queue, self.current_frame, cmap))

    def start(self):
        self._process.start()

    def request_frame(self, frame_index: int):
        self.current_frame.value = frame_index


def _data_process_run(
        provider: CsvDataProvider,
        ui_queue: Queue,
        current_frame: ValueProxy[int],
        cmap: Colormap):
    previous_frame = -1
    while True:
        if previous_frame == current_frame.value:
            time.sleep(0.01)
            continue
        previous_frame = current_frame.value
        df = provider.get_at(current_frame.value)
        if df is None:
            print("Skipped index: ", current_frame.value)
            time.sleep(0.01)
            continue

        ui_queue.put(df[["x", "y", "z"]].values)
        ui_queue.put(cmap(df["intensity"].values).astype(np.float64)[:, :3])  # type: ignore
