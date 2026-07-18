import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog
from typing import Callable

from .themes import COLORS, FONTS, SIZES
from ..utils.file_utils import get_file_info, get_category_icon, get_category_label, build_file_filter
from ..core.registry import ConverterRegistry
from ..core.base import FileCategory


class FilePanel(ctk.CTkFrame):
    def __init__(self, parent, on_files_added: Callable | None = None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_panel"], corner_radius=SIZES["border_radius"], **kwargs)

        self._on_files_added = on_files_added
        self._file_entries: list[dict] = []

        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_header"], corner_radius=0, height=40)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header, text="  Archivos", font=FONTS["heading"],
            text_color=COLORS["fg_header"], anchor="w"
        )
        title.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=4, pady=4)

        self._add_btn = ctk.CTkButton(
            btn_frame, text="+ Agregar", width=80, height=26,
            font=FONTS["small_bold"],
            fg_color=COLORS["accent_light"],
            text_color=COLORS["accent"],
            hover_color=COLORS["bg_header_hover"],
            corner_radius=3,
            command=self._add_files
        )
        self._add_btn.pack(side="left", padx=2)

        self._clear_btn = ctk.CTkButton(
            btn_frame, text="Limpiar", width=60, height=26,
            font=FONTS["small"],
            fg_color="transparent",
            text_color=COLORS["fg_header"],
            hover_color=COLORS["bg_header_hover"],
            corner_radius=3,
            command=self.clear_files
        )
        self._clear_btn.pack(side="left", padx=2)

        self._count_label = ctk.CTkLabel(
            self, text="0 archivos", font=FONTS["small"],
            text_color=COLORS["fg_muted"], anchor="w"
        )
        self._count_label.pack(fill="x", padx=10, pady=(6, 0))

        list_container = ctk.CTkFrame(self, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=6, pady=6)

        self._canvas = ctk.CTkScrollableFrame(
            list_container, fg_color=COLORS["bg_secondary"],
            corner_radius=SIZES["border_radius"]
        )
        self._canvas.pack(fill="both", expand=True)

        self._empty_label = ctk.CTkLabel(
            self._canvas,
            text="Arrastra archivos aqui\no haz clic en '+ Agregar'",
            font=FONTS["body"],
            text_color=COLORS["fg_muted"],
        )
        self._empty_label.pack(pady=40)

        self._drop_zone = ctk.CTkFrame(self, fg_color=COLORS["accent_light"], corner_radius=4, height=50)
        self._drop_zone.pack(fill="x", padx=6, pady=(0, 6))
        self._drop_zone.pack_propagate(False)

        drop_label = ctk.CTkLabel(
            self._drop_zone, text="Arrastra y suelta archivos aqui",
            font=FONTS["small"], text_color=COLORS["accent"]
        )
        drop_label.pack(expand=True)

    def _add_files(self):
        file_filter = build_file_filter()
        paths = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[(f.split(" (")[0], f.split("(")[1].rstrip(")")) for f in file_filter.split(";;")]
        )
        if paths:
            self.add_files([Path(p) for p in paths])

    def add_files(self, paths: list[Path]):
        self._empty_label.pack_forget()

        for path in paths:
            if not path.is_file():
                continue

            info = get_file_info(path)
            if info["category"] == FileCategory.UNKNOWN:
                continue

            valid_outputs = ConverterRegistry.get_valid_outputs(path.suffix)
            if not valid_outputs:
                continue

            entry = {
                "path": path,
                "info": info,
                "valid_outputs": valid_outputs,
            }
            self._file_entries.append(entry)
            self._create_file_row(entry)

        self._update_count()

        if self._on_files_added:
            self._on_files_added(self._file_entries)

    def _create_file_row(self, entry: dict):
        row = ctk.CTkFrame(self._canvas, fg_color=COLORS["bg_panel"], corner_radius=3, height=36)
        row.pack(fill="x", padx=2, pady=1)
        row.pack_propagate(False)

        info = entry["info"]
        icon = get_category_icon(info["category"])
        cat_color = COLORS.get(f"category_{info['category'].value}", COLORS["fg_primary"])

        icon_label = ctk.CTkLabel(row, text=icon, width=24, font=("Segoe UI Emoji", 13))
        icon_label.pack(side="left", padx=(6, 2))

        name_label = ctk.CTkLabel(
            row, text=info["name"], font=FONTS["small"],
            text_color=COLORS["fg_primary"], anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True, padx=2)

        badge = ctk.CTkLabel(
            row, text=info["extension"].upper(),
            font=FONTS["small_bold"], width=42, height=20,
            fg_color=cat_color, text_color="#FFFFFF",
            corner_radius=3
        )
        badge.pack(side="right", padx=(2, 6))

        entry["widget"] = row

    def _update_count(self):
        count = len(self._file_entries)
        self._count_label.configure(text=f"{count} archivo{'s' if count != 1 else ''}")

    def clear_files(self):
        for entry in self._file_entries:
            if "widget" in entry:
                entry["widget"].destroy()
        self._file_entries.clear()
        self._empty_label.pack(pady=40)
        self._update_count()

        if self._on_files_added:
            self._on_files_added([])

    def get_files(self) -> list[dict]:
        return list(self._file_entries)

    def remove_file(self, path: Path):
        self._file_entries = [e for e in self._file_entries if e["path"] != path]
        for entry in self._file_entries:
            if "widget" in entry and entry["path"] == path:
                entry["widget"].destroy()
        self._update_count()
        if not self._file_entries:
            self._empty_label.pack(pady=40)
