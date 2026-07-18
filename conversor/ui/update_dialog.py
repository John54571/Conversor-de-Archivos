import customtkinter as ctk
import threading
from pathlib import Path
from .themes import COLORS, FONTS, SIZES
from ..utils.update_checker import (
    ReleaseInfo,
    download_installer,
    run_installer,
    get_temp_installer_path,
    format_file_size,
)
from ..utils.config import config_manager
from ..utils.logger import logger


class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, release_info: ReleaseInfo):
        super().__init__(parent)
        self.title("Actualización disponible")
        self.geometry("500x400")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_primary"])
        
        self._release_info = release_info
        self._downloading = False
        
        self._build_ui()
        self.grab_set()

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame, text="Nueva versión disponible",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["fg_primary"]
        )
        title_label.pack(pady=(0, 10))

        version_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_group"], corner_radius=6)
        version_frame.pack(fill="x", pady=(0, 10))

        version_text = (
            f"Versión actual: {self._get_current_version()}\n"
            f"Nueva versión: {self._release_info.version}"
        )
        ctk.CTkLabel(
            version_frame, text=version_text,
            font=FONTS["body"], text_color=COLORS["fg_primary"],
            justify="left"
        ).pack(padx=12, pady=10)

        changelog_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_group"], corner_radius=6)
        changelog_frame.pack(fill="both", expand=True, pady=(0, 10))

        ctk.CTkLabel(
            changelog_frame, text="Cambios en esta versión:",
            font=FONTS["body_bold"], text_color=COLORS["fg_primary"],
            anchor="w"
        ).pack(fill="x", padx=12, pady=(8, 4))

        changelog_text = ctk.CTkTextbox(
            changelog_frame, font=FONTS["small"],
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["fg_primary"],
            corner_radius=4,
            wrap="word"
        )
        changelog_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        changelog_text.insert("1.0", self._release_info.body or "Sin changelog disponible")
        changelog_text.configure(state="disabled")

        self._progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self._progress_label = ctk.CTkLabel(
            self._progress_frame, text="",
            font=FONTS["small"], text_color=COLORS["fg_secondary"]
        )
        self._progress_label.pack(pady=(0, 4))

        self._progress_bar = ctk.CTkProgressBar(
            self._progress_frame, height=10,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["progress_fill"],
            corner_radius=5
        )
        self._progress_bar.pack(fill="x")
        self._progress_bar.set(0)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        self._update_btn = ctk.CTkButton(
            button_frame, text="Actualizar ahora",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", width=140,
            command=self._start_update
        )
        self._update_btn.pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="Más tarde",
            font=FONTS["body"],
            fg_color=COLORS["button_bg"], hover_color=COLORS["button_hover"],
            text_color=COLORS["fg_primary"], width=100,
            command=self.destroy
        ).pack(side="right", padx=5)

        self._skip_check_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            button_frame, text="No volver a preguntar esta versión",
            variable=self._skip_check_var,
            font=FONTS["small"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"]
        ).pack(side="bottom", pady=(10, 0))

    def _get_current_version(self) -> str:
        from ..utils.update_checker import get_current_version
        return get_current_version()

    def _start_update(self):
        if self._downloading:
            return
        
        self._downloading = True
        self._update_btn.configure(state="disabled", text="Descargando...")
        self._progress_frame.pack(fill="x", pady=(10, 0))

        def download_thread():
            installer_path = get_temp_installer_path()
            
            def on_progress(progress, downloaded, total):
                self.after(0, lambda: self._update_progress(progress, downloaded, total))
            
            success = download_installer(
                self._release_info.installer_url,
                installer_path,
                on_progress
            )
            
            if success:
                self.after(0, lambda: self._on_download_complete(installer_path))
            else:
                self.after(0, self._on_download_failed)

        threading.Thread(target=download_thread, daemon=True).start()

    def _update_progress(self, progress: float, downloaded: int, total: int):
        self._progress_bar.set(progress)
        downloaded_str = format_file_size(downloaded)
        total_str = format_file_size(total)
        self._progress_label.configure(text=f"Descargando: {downloaded_str} / {total_str}")

    def _on_download_complete(self, installer_path: Path):
        self._progress_label.configure(text="Descarga completada. Iniciando instalador...")
        
        if self._skip_check_var.get():
            config_manager.update_config(last_ignored_version=self._release_info.version)
        
        if run_installer(installer_path):
            self.after(500, self._close_app)
        else:
            self._on_download_failed()

    def _on_download_failed(self):
        self._progress_label.configure(text="Error al descargar. Intenta de nuevo.", text_color=COLORS["error"])
        self._update_btn.configure(state="normal", text="Reintentar")
        self._downloading = False

    def _close_app(self):
        self.destroy()
        self.master.quit()
