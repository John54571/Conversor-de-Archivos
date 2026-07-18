import customtkinter as ctk
from pathlib import Path
from .themes import COLORS, FONTS, SIZES
from ..utils.logger import logger


class LogViewerWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Visor de Logs")
        self.geometry("700x500")
        self.configure(fg_color=COLORS["bg_primary"])
        
        self._build_ui()
        self._load_log_list()
        
        self.grab_set()

    def _build_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        left = ctk.CTkFrame(main, fg_color=COLORS["bg_panel"], corner_radius=4, width=200)
        left.pack(side="left", fill="y", padx=(0, 6))
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="Archivos de log", font=FONTS["body_bold"],
                     text_color=COLORS["fg_primary"]).pack(fill="x", padx=8, pady=(8, 4))

        self._log_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self._log_list.pack(fill="both", expand=True, padx=4, pady=4)

        right = ctk.CTkFrame(main, fg_color=COLORS["bg_panel"], corner_radius=4)
        right.pack(side="right", fill="both", expand=True)

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 4))

        ctk.CTkLabel(header, text="Contenido del log", font=FONTS["body_bold"],
                     text_color=COLORS["fg_primary"]).pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(btn_frame, text="Actualizar", width=80, height=26,
                      font=FONTS["small"], fg_color=COLORS["button_bg"],
                      hover_color=COLORS["button_hover"],
                      command=self._refresh_log).pack(side="left", padx=2)

        ctk.CTkButton(btn_frame, text="Limpiar todo", width=80, height=26,
                      font=FONTS["small"], fg_color=COLORS["error"],
                      hover_color="#B71C1C",
                      command=self._clear_all_logs).pack(side="left", padx=2)

        self._log_text = ctk.CTkTextbox(
            right, font=FONTS["mono"], fg_color=COLORS["bg_secondary"],
            text_color=COLORS["fg_primary"], corner_radius=4,
            wrap="word"
        )
        self._log_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _load_log_list(self):
        for widget in self._log_list.winfo_children():
            widget.destroy()

        log_files = logger.get_log_files()
        
        if not log_files:
            ctk.CTkLabel(self._log_list, text="No hay logs disponibles",
                        font=FONTS["small"], text_color=COLORS["fg_muted"]).pack(pady=20)
            return

        for log_file in log_files[:20]:
            btn = ctk.CTkButton(
                self._log_list, text=log_file.stem.replace("conversor_", ""),
                font=FONTS["small"], fg_color="transparent",
                text_color=COLORS["fg_primary"],
                hover_color=COLORS["accent_light"],
                anchor="w", height=28,
                command=lambda f=log_file: self._show_log(f)
            )
            btn.pack(fill="x", padx=2, pady=1)

        if log_files:
            self._show_log(log_files[0])

    def _show_log(self, log_file: Path):
        self._log_text.delete("1.0", "end")
        content = logger.read_log(log_file, lines=500)
        self._log_text.insert("1.0", content)

    def _refresh_log(self):
        self._load_log_list()

    def _clear_all_logs(self):
        log_dir = logger.get_log_dir()
        for log_file in log_dir.glob("conversor_*.log"):
            try:
                log_file.unlink()
            except Exception:
                pass
        self._load_log_list()
        self._log_text.delete("1.0", "end")
        self._log_text.insert("1.0", "Todos los logs han sido eliminados.")
