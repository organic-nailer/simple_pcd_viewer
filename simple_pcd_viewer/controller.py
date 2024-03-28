import customtkinter as tk
from tkfontawesome import icon_to_image

from simple_pcd_viewer.data_process import DataProcess
from simple_pcd_viewer.window import PcdUiProcess


class TkController:
    def __init__(self, ui: PcdUiProcess, data_process: DataProcess, debug: bool = False):
        if debug:
            print("TkController.__init__")
        self.debug = debug
        self.ui = ui
        self.data_process = data_process
        self.app = tk.CTk()
        self.index: tk.IntVar = tk.IntVar(value=0)
        self.current_index_str = tk.StringVar(value=str(0))
        self.index.trace_add("write", lambda *_: self.current_index_str.set(str(self.index.get())))
        self.playing = tk.BooleanVar(value=False)
        self.play_id = None
        self.point_size_str = tk.StringVar(value="-")
        self.line_width_str = tk.StringVar(value="-")
        self.background_color_str = tk.StringVar(value="-")
        self.intrinsics_str = tk.StringVar(value="-")
        self.extrinsics_str = tk.StringVar(value="-")
        self.fov_str = tk.StringVar(value="-")

    def play_pause(self):
        self.playing.set(not self.playing.get())
        if self.debug:
            print("TkController.play_pause:", self.playing.get())
        if self.playing.get():
            self.button_play_pause.configure(image=icon_to_image("pause", fill="white", scale_to_height=24))

            def play():
                if self.index.get() >= self.data_process.config.frame_num - 1:
                    self.playing.set(False)
                    self.button_play_pause.configure(image=icon_to_image("play", fill="white", scale_to_height=24))
                    return
                self.move_to(self.index.get() + 1)
                if self.playing.get():
                    self.play_id = self.app.after(int(1000 / self.data_process.config.fps), play)
            self.play_id = self.app.after(int(1000 / self.data_process.config.fps), play)
        else:
            if self.play_id is not None:
                self.app.after_cancel(self.play_id)
                self.play_id = None
            self.button_play_pause.configure(image=icon_to_image("play", fill="white", scale_to_height=24))

    def move_to(self, index: int):
        if self.debug:
            print("TkController.move_to:", index)
        if index < 0:
            index = 0
        if index >= self.data_process.config.frame_num:
            index = self.data_process.config.frame_num - 1
        self.index.set(index)
        self.data_process.request_frame(index)

    def show(self):
        if self.debug:
            print("TkController.show")
        self.app.title("Simple PCD Controller")
        self.app.geometry("600x300")
        self.app.attributes('-topmost', True)  # Always on top

        self.app.columnconfigure(0, weight=1)
        self.app.columnconfigure(1, weight=1)
        self.app.columnconfigure(2, weight=1)
        self.app.columnconfigure(3, weight=1)
        self.app.columnconfigure(4, weight=1)
        button_to_first = tk.CTkButton(
            self.app,
            text="",
            width=48,
            height=48,
            image=icon_to_image("step-backward", fill="white", scale_to_height=24),
            command=lambda: self.move_to(0))
        button_to_first.grid(row=0, column=0)
        button_previous = tk.CTkButton(
            self.app,
            text="",
            width=48,
            height=48,
            image=icon_to_image("chevron-left", fill="white", scale_to_height=24),
            command=lambda: self.move_to(self.index.get() - 1))
        button_previous.grid(row=0, column=1)
        self.button_play_pause = tk.CTkButton(
            self.app,
            text="",
            width=48,
            height=48,
            image=icon_to_image("play", fill="white", scale_to_height=24),
            command=self.play_pause)
        self.button_play_pause.grid(row=0, column=2)
        button_next = tk.CTkButton(
            self.app,
            text="",
            width=48,
            height=48,
            image=icon_to_image("chevron-right", fill="white", scale_to_height=24),
            command=lambda: self.move_to(self.index.get() + 1))
        button_next.grid(row=0, column=3)
        button_to_last = tk.CTkButton(
            self.app,
            text="",
            width=48,
            height=48,
            image=icon_to_image("step-forward", fill="white", scale_to_height=24),
            command=lambda: self.move_to(self.data_process.config.frame_num - 1))
        button_to_last.grid(row=0, column=4)

        label = tk.CTkLabel(self.app, textvariable=self.current_index_str)
        label.grid(row=1, column=0)
        slider = tk.CTkSlider(
            self.app,
            variable=self.index,
            from_=0, to=self.data_process.config.frame_num - 1,
            number_of_steps=self.data_process.config.frame_num,
            command=lambda value: self.move_to(int(value)))
        slider.grid(row=1, column=1, columnspan=4, sticky="ew")

        tk.CTkLabel(self.app, text="Point Size:").grid(row=2, column=0)
        tk.CTkLabel(self.app, textvariable=self.point_size_str).grid(row=2, column=1, columnspan=4, sticky="ew")
        tk.CTkLabel(self.app, text="Line Width:").grid(row=3, column=0)
        tk.CTkLabel(self.app, textvariable=self.line_width_str).grid(row=3, column=1, columnspan=4, sticky="ew")
        tk.CTkLabel(self.app, text="Background Color:").grid(row=4, column=0)
        tk.CTkLabel(self.app, textvariable=self.background_color_str).grid(row=4, column=1, columnspan=4, sticky="ew")
        tk.CTkLabel(self.app, text="Intrinsics:").grid(row=5, column=0)
        tk.CTkLabel(self.app, textvariable=self.intrinsics_str).grid(row=5, column=1, columnspan=4, sticky="ew")
        tk.CTkLabel(self.app, text="Extrinsics:").grid(row=6, column=0)
        tk.CTkLabel(self.app, textvariable=self.extrinsics_str).grid(row=6, column=1, columnspan=4, sticky="ew")
        tk.CTkLabel(self.app, text="FoV:").grid(row=7, column=0)
        tk.CTkLabel(self.app, textvariable=self.fov_str).grid(row=7, column=1, columnspan=4, sticky="ew")

        def observe_pcd_ui():
            if self.ui.window_close_event.is_set():
                self.app.quit()
                return
            status = self.ui.current_status
            if status is None:
                self.app.after(100, observe_pcd_ui)
                return
            if "point_size" in status:
                self.point_size_str.set(str(status["point_size"]))
            if "line_width" in status:
                self.line_width_str.set(str(status["line_width"]))
            if "background_color" in status:
                self.background_color_str.set(str(status["background_color"]))
            if "intrinsics" in status:
                self.intrinsics_str.set(str(status["intrinsics"]))
            if "extrinsics" in status:
                self.extrinsics_str.set(str(status["extrinsics"]))
            if "fov" in status:
                self.fov_str.set(str(status["fov"]))
            self.app.after(100, observe_pcd_ui)

        observe_pcd_ui()
        self.app.mainloop()
