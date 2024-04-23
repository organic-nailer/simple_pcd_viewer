import numpy as np
from .tk_controller import TkController
from .csv_data_provider import CsvDataProvider, PcdFilter, PcdTransformer
from .process_data import PcdDataProcess
from .process_pcd_ui import PcdUiProcess
from .pcd_data_config import PcdDataConfig


class CsvVisualizer:
    def __init__(
            self,
            dir: str,
            name: str,
            length: int,
            filter: PcdFilter,
            transformer: PcdTransformer,
            debug: bool = False):
        if debug:
            print("CsvVisualizer.__init__")
        self.debug = debug
        self.name = name
        self.length = length
        self.data_provider = CsvDataProvider(
            dir, name, length,
            filter,
            transformer,
            debug)

    def show(self):
        np.set_printoptions(precision=2, suppress=True)

        ui = PcdUiProcess(debug=self.debug)
        config: PcdDataConfig = PcdDataConfig(self.name, 57600, self.length, 10.0)
        data_process = PcdDataProcess(ui, [self.data_provider], config, self.debug)

        try:
            data_process._process.start()

            controller = TkController(ui, data_process, self.debug)
            controller.show()

            # MainApp().run()
        finally:
            ui.close()
            data_process._process.terminate()
            ui.join()
