import matplotlib
import numpy as np
from simple_pcd_viewer.controller import TkController
from simple_pcd_viewer.csv_data_provider import CsvDataProvider, PcdFilter, PcdTransformer
from simple_pcd_viewer.data_process import DataProcess
from simple_pcd_viewer.window import PcdUiProcess


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
        self.data_provider = CsvDataProvider(
            dir, name, length,
            filter,
            transformer,
            debug)

    def show(self):
        np.set_printoptions(precision=2, suppress=True)

        ui = PcdUiProcess(debug=self.debug)
        data_process = DataProcess(ui, self.data_provider, matplotlib.colormaps["cool"], self.debug)

        try:
            data_process._process.start()

            controller = TkController(ui, data_process, self.debug)
            controller.show()

            # MainApp().run()
        finally:
            ui.close()
            data_process._process.terminate()
            ui.join()
