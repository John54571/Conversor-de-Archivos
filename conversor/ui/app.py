import customtkinter as ctk
from pathlib import Path
import threading
import sys
import os

from .themes import COLORS, FONTS, SIZES
from .file_panel import FilePanel
from .options_panel import OptionsPanel
from .progress_panel import ProgressPanel
from .preview_panel import PreviewPanel
from .settings_window import SettingsWindow
from .log_viewer import LogViewerWindow
from .history_window import HistoryWindow
from ..core.engine import ConversionEngine
from ..converters.base import ConversionTask, ConversionOptions, ConversionStatus
from ..utils.ffmpeg_check import check_ffmpeg, check_ffmpeg_version
from ..utils.config import config_manager
from ..utils.logger import logger
from ..utils.zip_utils import create_zip_from_files
from ..utils.windows_integration import register_windows_context_menu, unregister_windows_context_menu, is_context_menu_registered, handle_command_line_args
from ..utils.update_checker import check_for_updates


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Conversor de Archivos")
        self.geometry(f"{SIZES['min_width']}x{SIZES['min_height']}")
        self.minsize(SIZES["min_width"], SIZES["min_height"])
        self.configure(fg_color=COLORS["bg_primary"])

        self._set_icon()

        config = config_manager.get_config()
        self._engine = ConversionEngine(max_workers=config.max_workers)
        self._engine.set_on_task_update(self._on_task_update)

        self._build_ui()
        self._check_dependencies()
        self._ensure_context_menu()
        self._handle_cli_args()
        self._setup_scaling()
        self._check_updates_on_startup()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_icon(self):
        try:
            if getattr(sys, "frozen", False):
                base_path = os.path.join(sys._MEIPASS, "conversor", "assets")
            else:
                base_path = str(Path(__file__).parent.parent / "assets")
            
            icon_path = os.path.join(base_path, "iconochoro.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_header"], corner_radius=0, height=60)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        logo = ctk.CTkLabel(
            top_bar, text="  Conversor de Archivos",
            font=FONTS["title"], text_color=COLORS["fg_header"], anchor="w"
        )
        logo.pack(side="left", padx=12, pady=8)

        menu_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        menu_frame.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            menu_frame, text="Ajustes", width=70, height=28,
            font=FONTS["small"], fg_color="transparent",
            text_color=COLORS["fg_header"],
            hover_color=COLORS["bg_header_hover"],
            command=self._open_settings
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            menu_frame, text="Historial", width=70, height=28,
            font=FONTS["small"], fg_color="transparent",
            text_color=COLORS["fg_header"],
            hover_color=COLORS["bg_header_hover"],
            command=self._open_history
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            menu_frame, text="Logs", width=60, height=28,
            font=FONTS["small"], fg_color="transparent",
            text_color=COLORS["fg_header"],
            hover_color=COLORS["bg_header_hover"],
            command=self._open_logs
        ).pack(side="left", padx=2)

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

        self._file_panel = FilePanel(
            left,
            on_files_added=self._on_files_changed,
            on_file_selected=self._on_file_selected
        )
        self._file_panel.pack(fill="both", expand=True)

        center = ctk.CTkFrame(main, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True, padx=4)

        self._options_panel = OptionsPanel(center, on_convert=self._on_convert)
        self._options_panel.pack(fill="both", expand=True)

        right = ctk.CTkFrame(main, fg_color="transparent", width=320)
        right.pack(side="right", fill="both", expand=True, padx=(4, 0))

        right_top = ctk.CTkFrame(right, fg_color="transparent")
        right_top.pack(fill="both", expand=True)

        self._progress_panel = ProgressPanel(right_top)
        self._progress_panel.pack(fill="both", expand=True)
        self._progress_panel.set_callbacks(
            on_cancel_all=self._cancel_all,
            on_clear_completed=self._clear_completed
        )

        config = config_manager.get_config()
        if config.show_preview:
            right_bottom = ctk.CTkFrame(right, fg_color="transparent", height=280)
            right_bottom.pack(fill="x", pady=(6, 0))
            right_bottom.pack_propagate(False)

            self._preview_panel = PreviewPanel(right_bottom)
            self._preview_panel.pack(fill="both", expand=True)
        else:
            self._preview_panel = None

    def _check_dependencies(self):
        if check_ffmpeg():
            self._ffmpeg_status.configure(text="Aplicación creada por John", text_color=COLORS["fg_header"])
        else:
            self._ffmpeg_status.configure(
                text="FFmpeg no encontrado (audio/video no disponibles)",
                text_color="#FFB6B6"
            )

    def _ensure_context_menu(self):
        if sys.platform == "win32" and not is_context_menu_registered():
            try:
                register_windows_context_menu()
            except Exception:
                pass

    def _setup_scaling(self):
        self._base_width = SIZES["min_width"]
        self._scale_factor = 1.0
        self.bind("<Configure>", self._on_window_resize)

    def _on_window_resize(self, event):
        if event.widget != self:
            return
        new_width = self.winfo_width()
        new_scale = max(1.0, new_width / self._base_width)
        if abs(new_scale - self._scale_factor) > 0.05:
            self._scale_factor = new_scale
            self.after(100, self._update_scaling)

    def _update_scaling(self):
        scale = self._scale_factor
        new_fonts = {
            "title": ("Segoe UI", int(20 * scale), "bold"),
            "heading": ("Segoe UI", int(16 * scale), "bold"),
            "body": ("Segoe UI", int(13 * scale)),
            "body_bold": ("Segoe UI", int(13 * scale), "bold"),
            "small": ("Segoe UI", int(11 * scale)),
            "small_bold": ("Segoe UI", int(11 * scale), "bold"),
            "mono": ("Consolas", int(12 * scale)),
        }
        FONTS.update(new_fonts)

    def _check_updates_on_startup(self):
        def _do_check():
            release_info = check_for_updates()
            if release_info:
                self.after(0, lambda: self._show_update_dialog(release_info))

        threading.Thread(target=_do_check, daemon=True).start()

    def _show_update_dialog(self, release_info):
        from .update_dialog import UpdateDialog
        UpdateDialog(self, release_info)

    def _handle_cli_args(self):
        file_path = handle_command_line_args()
        if file_path:
            self.after(500, lambda: self._file_panel.add_files([file_path]))

    def _on_files_changed(self, file_entries: list[dict]):
        self._options_panel.update_files(file_entries)

    def _on_file_selected(self, file_path: Path):
        if self._preview_panel:
            self._preview_panel.show_preview(file_path)

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
        estimated_time = self._engine.get_estimated_time_remaining()
        self._progress_panel.update_global(summary, estimated_time)

        active = self._engine.get_active_tasks()
        if active:
            self.after(300, self._poll_progress)
        else:
            self._progress_panel.update_global(summary, 0.0)
            self._options_panel.set_converting(False)

            config = config_manager.get_config()
            if config.create_zip_on_batch:
                completed_tasks = [t for t in self._engine.get_all_tasks() if t.status == ConversionStatus.COMPLETED]
                if len(completed_tasks) > 1:
                    self._create_zip_from_completed(completed_tasks)

    def _create_zip_from_completed(self, tasks: list[ConversionTask]):
        output_files = [t.output_path for t in tasks if t.output_path and t.output_path.exists()]
        if output_files:
            output_dir = output_files[0].parent
            zip_path = output_dir / "conversion_result.zip"
            
            def _do_zip():
                create_zip_from_files(output_files, zip_path)
                logger.info(f"ZIP creado: {zip_path}")
            
            threading.Thread(target=_do_zip, daemon=True).start()

    def _on_task_update(self, task: ConversionTask):
        self.after(0, lambda: self._progress_panel.update_task(task))

    def _cancel_all(self):
        self._engine.cancel_all()
        self._options_panel.set_converting(False)

    def _clear_completed(self):
        self._engine.clear_completed()
        self._progress_panel.clear_all()

    def _open_settings(self):
        SettingsWindow(self)

    def _open_history(self):
        HistoryWindow(self)

    def _open_logs(self):
        LogViewerWindow(self)

    def _on_close(self):
        self._engine.shutdown(wait=False)
        self.destroy()
