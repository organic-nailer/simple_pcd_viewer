from typing import Optional
import time

from simple_pcd_viewer.pcd_data_config import PcdDataConfig
from simple_pcd_viewer.process_pcd_ui import PcdUiProcess
from simple_pcd_viewer.single.single_data_provider import DataType, PcdReadingRule, SingleDataProvider
from simple_pcd_viewer.process_data import PcdDataProcess
from simple_pcd_viewer.tk_controller import TkController

class SingleFrameVisualizer:
    def __init__(
            self,
            data: DataType,
            rule: Optional[PcdReadingRule] = None,
            debug: bool = False):
        if debug:
            print("SingleFrameVisualizer.__init__")
        self.debug = debug
        self.data = data
        self.rule = rule if rule is not None else PcdReadingRule()

    def show(self, show_controller: bool = True):
        provider = SingleDataProvider(self.data, self.rule, debug=self.debug)

        ui = PcdUiProcess(debug=self.debug)
        config: PcdDataConfig = PcdDataConfig("single", 57600, 1, 10.0)
        data_process = PcdDataProcess(ui, [provider], config, first_frame=0, debug=self.debug)

        try:
            data_process.start()

            if show_controller:
                controller = TkController(ui, data_process, self.debug)
                controller.show()
            else:
                while not ui.window_close_event.is_set():
                    time.sleep(0.5)
                    pass

        finally:
            ui.close()
            data_process._process.terminate()
            ui.join()
