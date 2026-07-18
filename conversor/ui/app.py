import customtkinter as ctk
from pathlib import Path
import threading

from .themes import COLORS, FONTS, SIZES
from .file_panel import FilePanel
from .options_panel import OptionsPanel
from .progress_panel import ProgressPanel
from ..core.engine import ConversionEngine
from ..core.base import ConversionTask, ConversionOptions, ConversionStatus
from ..utils.ffmpeg_check import check_ffmpeg, check_ffmpeg_version


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Conversor de Archivos")
        self.geometry(f"{SIZES['min_width']}x{SIZES['min_height']}")
        self.minsize(SIZES["min_width"], SIZES["min_height"])
        self.configure(fg_color=COLORS["bg_primary"])

        self._engine = ConversionEngine(max_workers=3)
        self._engine.set_on_task_update(self._on_task_update)

        self._build_ui()
        self._check_dependencies()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_header"], corner_radius=0, height=48)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        logo = ctk.CTkLabel(
            top_bar, text="  Conversor de Archivos",
            font=FONTS["title"], text_color=COLORS["fg_header"], anchor="w"
        )
        logo.pack(side="left", padx=12, pady=8)

        self._ffmpeg_status = ctk.CTkLabel(
            top_bar, text="", font=FONTS["small"],
            text_color=COLORS["fg_header"], anchor="e"
        )
        self._ffmpeg_status.pack(side="right", padx=12)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=8, pady=8)

        left = ctk.CTkFrame(main, fg_color="transparent", width=360)
        left.pack(side="left", fill="y", padx=(0, 4))
        left.pack_propagate(False)

        self._file_panel = FilePanel(left, on_files_added=self._on_files_changed)
        self._file_panel.pack(fill="both", expand=True)

        center = ctk.CTkFrame(main, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True, padx=4)

        self._options_panel = OptionsPanel(center, on_convert=self._on_convert)
        self._options_panel.pack(fill="both", expand=True)

        right = ctk.CTkFrame(main, fg_color="transparent", width=320)
        right.pack(side="right", fill="both", expand=True, padx=(4, 0))

        self._progress_panel = ProgressPanel(right)
        self._progress_panel.pack(fill="both", expand=True)
        self._progress_panel.set_callbacks(
            on_cancel_all=self._cancel_all,
            on_clear_completed=self._clear_completed
        )

    def _check_dependencies(self):
        if check_ffmpeg():
            version = check_ffmpeg_version()
            short = version.split(",")[0] if version else "OK"
            self._ffmpeg_status.configure(text=f"FFmpeg: {short}", text_color="#90EE90")
        else:
            self._ffmpeg_status.configure(
                text="FFmpeg no encontrado (audio/video no disponibles)",
                text_color="#FFB6B6"
            )

    def _on_files_changed(self, file_entries: list[dict]):
        self._options_panel.update_files(file_entries)

    def _on_convert(self, conversion_plan: list[dict]):
        self._progress_panel.clear_all()
        self._options_panel.set_converting(True)

        tasks = []
        for item in conversion_plan:
            entry = item["entry"]
            options = item["options"]
            task = self._engine.create_task(
                source_path=entry["path"],
                output_format=options.output_format,
                options=options,
            )
            self._progress_panel.add_task(task)
            tasks.append(task)

        self._engine.submit_batch(tasks)

        self._poll_progress()

    def _poll_progress(self):
        summary = self._engine.get_summary()
        self._progress_panel.update_global(summary)

        active = self._engine.get_active_tasks()
        if active:
            self.after(300, self._poll_progress)
        else:
            self._progress_panel.update_global(summary)
            self._options_panel.set_converting(False)

    def _on_task_update(self, task: ConversionTask):
        self.after(0, lambda: self._progress_panel.update_task(task))

    def _cancel_all(self):
        self._engine.cancel_all()
        self._options_panel.set_converting(False)

    def _clear_completed(self):
        self._engine.clear_completed()
        self._progress_panel.clear_all()

    def _on_close(self):
        self._engine.shutdown(wait=False)
        self.destroy()
