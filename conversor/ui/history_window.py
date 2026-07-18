import customtkinter as ctk
from .themes import COLORS, FONTS, SIZES
from ..utils.config import config_manager
from ..utils.file_utils import format_file_size


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Historial de Conversiones")
        self.geometry("750x500")
        self.configure(fg_color=COLORS["bg_primary"])
        
        self._build_ui()
        self._load_history()
        
        self.grab_set()

    def _build_ui(self):
        stats_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_group"], corner_radius=6)
        stats_frame.pack(fill="x", padx=12, pady=(12, 6))

        stats = config_manager.get_history_stats()
        
        stats_text = (
            f"Total: {stats['total']}  |  "
            f"Exitosas: {stats['successful']}  |  "
            f"Fallidas: {stats['failed']}  |  "
            f"Espacio ahorrado: {format_file_size(stats['total_size_saved'])}"
        )
        ctk.CTkLabel(stats_frame, text=stats_text, font=FONTS["body"],
                     text_color=COLORS["fg_primary"]).pack(padx=12, pady=8)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(header_frame, text="Historial", font=FONTS["heading"],
                     text_color=COLORS["fg_primary"]).pack(side="left")

        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(btn_frame, text="Actualizar", width=80, height=26,
                      font=FONTS["small"], fg_color=COLORS["button_bg"],
                      hover_color=COLORS["button_hover"],
                      command=self._load_history).pack(side="left", padx=2)

        ctk.CTkButton(btn_frame, text="Limpiar historial", width=110, height=26,
                      font=FONTS["small"], fg_color=COLORS["error"],
                      hover_color="#B71C1C",
                      command=self._clear_history).pack(side="left", padx=2)

        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=4)
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        col_header = ctk.CTkFrame(table_frame, fg_color=COLORS["bg_header"], corner_radius=0, height=30)
        col_header.pack(fill="x")
        col_header.pack_propagate(False)

        columns = [("Archivo", 200), ("Conversion", 120), ("Estado", 80), ("Duracion", 70), ("Fecha", 140)]
        for text, width in columns:
            ctk.CTkLabel(col_header, text=text, font=FONTS["small_bold"],
                        text_color=COLORS["fg_header"], width=width).pack(side="left", padx=4)

        self._scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)

    def _load_history(self):
        for widget in self._scroll.winfo_children():
            widget.destroy()

        history = config_manager.get_history()
        
        if not history:
            ctk.CTkLabel(self._scroll, text="No hay conversiones en el historial",
                        font=FONTS["body"], text_color=COLORS["fg_muted"]).pack(pady=30)
            return

        for record in history[:100]:
            row = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_secondary"], corner_radius=3, height=28)
            row.pack(fill="x", padx=2, pady=1)
            row.pack_propagate(False)

            source_name = record.source_path.split("\\")[-1] if "\\" in record.source_path else record.source_path.split("/")[-1]
            ctk.CTkLabel(row, text=source_name[:30], font=FONTS["small"],
                        text_color=COLORS["fg_primary"], width=200, anchor="w").pack(side="left", padx=4)

            conv_text = f"{record.source_format.upper()} -> {record.output_format.upper()}"
            ctk.CTkLabel(row, text=conv_text, font=FONTS["small"],
                        text_color=COLORS["fg_secondary"], width=120).pack(side="left", padx=4)

            status_color = COLORS["success"] if record.status == "completed" else COLORS["error"]
            status_text = "OK" if record.status == "completed" else "Error"
            ctk.CTkLabel(row, text=status_text, font=FONTS["small_bold"],
                        text_color=status_color, width=80).pack(side="left", padx=4)

            duration_text = f"{record.duration:.1f}s"
            ctk.CTkLabel(row, text=duration_text, font=FONTS["small"],
                        text_color=COLORS["fg_secondary"], width=70).pack(side="left", padx=4)

            date_text = record.timestamp[:16].replace("T", " ")
            ctk.CTkLabel(row, text=date_text, font=FONTS["small"],
                        text_color=COLORS["fg_muted"], width=140).pack(side="left", padx=4)

    def _clear_history(self):
        config_manager.clear_history()
        self._load_history()
