import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog
from typing import Callable

from .themes import COLORS, FONTS, SIZES
from ..core.registry import ConverterRegistry
from ..converters.base import FileCategory, ConversionOptions
from ..utils.file_utils import get_category_label


class OptionsPanel(ctk.CTkFrame):
    def __init__(self, parent, on_convert: Callable | None = None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_panel"], corner_radius=SIZES["border_radius"], **kwargs)

        self._on_convert = on_convert
        self._file_entries: list[dict] = []
        self._format_vars: dict[str, ctk.StringVar] = {}
        self._quality_var = ctk.StringVar(value="")
        self._output_dir = ctk.StringVar(value="")
        self._same_as_source = ctk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_header"], corner_radius=0, height=40)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header, text="  Opciones de conversion", font=FONTS["heading"],
            text_color=COLORS["fg_header"], anchor="w"
        )
        title.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=6, pady=6)

        self._empty_label = ctk.CTkLabel(
            self._scroll, text="Agrega archivos para\nver las opciones",
            font=FONTS["body"], text_color=COLORS["fg_muted"]
        )
        self._empty_label.pack(pady=40)

        self._format_section = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_group"], corner_radius=4)

        fmt_title = ctk.CTkLabel(
            self._format_section, text="Formato de destino",
            font=FONTS["body_bold"], text_color=COLORS["fg_primary"], anchor="w"
        )
        fmt_title.pack(fill="x", padx=10, pady=(8, 4))

        self._format_frame = ctk.CTkFrame(self._format_section, fg_color="transparent")
        self._format_frame.pack(fill="x", padx=10, pady=(0, 8))

        self._quality_section = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_group"], corner_radius=4)

        quality_title = ctk.CTkLabel(
            self._quality_section, text="Calidad",
            font=FONTS["body_bold"], text_color=COLORS["fg_primary"], anchor="w"
        )
        quality_title.pack(fill="x", padx=10, pady=(8, 4))

        self._quality_menu = ctk.CTkOptionMenu(
            self._quality_section, variable=self._quality_var,
            values=["Sin ajustes"], font=FONTS["body"],
            fg_color=COLORS["bg_panel"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_panel"],
            width=200, height=30
        )
        self._quality_menu.pack(fill="x", padx=10, pady=(0, 8))

        self._output_section = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_group"], corner_radius=4)

        out_title = ctk.CTkLabel(
            self._output_section, text="Carpeta de destino",
            font=FONTS["body_bold"], text_color=COLORS["fg_primary"], anchor="w"
        )
        out_title.pack(fill="x", padx=10, pady=(8, 4))

        same_radio = ctk.CTkRadioButton(
            self._output_section, text="Misma carpeta de origen",
            variable=self._same_as_source, value=True,
            font=FONTS["body"], text_color=COLORS["fg_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._toggle_output
        )
        same_radio.pack(fill="x", padx=10, pady=2)

        custom_radio = ctk.CTkRadioButton(
            self._output_section, text="Carpeta personalizada:",
            variable=self._same_as_source, value=False,
            font=FONTS["body"], text_color=COLORS["fg_primary"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._toggle_output
        )
        custom_radio.pack(fill="x", padx=10, pady=2)

        dir_frame = ctk.CTkFrame(self._output_section, fg_color="transparent")
        dir_frame.pack(fill="x", padx=10, pady=(2, 8))

        self._dir_entry = ctk.CTkEntry(
            dir_frame, textvariable=self._output_dir,
            font=FONTS["small"], state="disabled",
            fg_color=COLORS["bg_secondary"], border_color=COLORS["border"],
            height=28
        )
        self._dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self._browse_btn = ctk.CTkButton(
            dir_frame, text="...", width=30, height=28,
            font=FONTS["small_bold"],
            fg_color=COLORS["button_bg"], hover_color=COLORS["button_hover"],
            text_color=COLORS["fg_primary"], corner_radius=3,
            state="disabled", command=self._browse_output
        )
        self._browse_btn.pack(side="right")

        self._summary_frame = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_group"], corner_radius=4)

        self._summary_label = ctk.CTkLabel(
            self._summary_frame, text="", font=FONTS["small"],
            text_color=COLORS["fg_secondary"], justify="left"
        )
        self._summary_label.pack(fill="x", padx=10, pady=8)

        self._convert_btn = ctk.CTkButton(
            self, text="CONVERTIR", font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#000000", text_color_disabled="#000000",
            height=40, corner_radius=SIZES["border_radius"],
            command=self._trigger_convert
        )
        self._convert_btn.pack(fill="x", padx=10, pady=10)
        self._convert_btn.configure(state="disabled")

    def _toggle_output(self):
        if self._same_as_source.get():
            self._dir_entry.configure(state="disabled")
            self._browse_btn.configure(state="disabled")
        else:
            self._dir_entry.configure(state="normal")
            self._browse_btn.configure(state="normal")

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if folder:
            self._output_dir.set(folder)

    def update_files(self, file_entries: list[dict]):
        self._file_entries = file_entries
        self._format_vars.clear()

        for widget in self._format_section.winfo_children():
            if widget.winfo_name() != "!ctklabel":
                widget.destroy()

        if not file_entries:
            self._format_section.pack_forget()
            self._quality_section.pack_forget()
            self._output_section.pack_forget()
            self._summary_frame.pack_forget()
            self._empty_label.pack(pady=40)
            self._convert_btn.configure(state="disabled")
            return

        self._empty_label.pack_forget()

        categories_seen: dict[str, list[dict]] = {}
        for entry in file_entries:
            cat = entry["info"]["category"].value
            if cat not in categories_seen:
                categories_seen[cat] = []
            categories_seen[cat].append(entry)

        fmt_title = ctk.CTkLabel(
            self._format_section, text="Formato de destino",
            font=FONTS["body_bold"], text_color=COLORS["fg_primary"], anchor="w"
        )
        fmt_title.pack(fill="x", padx=10, pady=(8, 4))

        for cat_key, entries in categories_seen.items():
            cat_label = get_category_label(FileCategory(cat_key))
            cat_color = COLORS.get(f"category_{cat_key}", COLORS["fg_primary"])

            cat_header = ctk.CTkLabel(
                self._format_section, text=f"  {cat_label} ({len(entries)})",
                font=FONTS["small_bold"], text_color=cat_color, anchor="w"
            )
            cat_header.pack(fill="x", padx=10, pady=(4, 0))

            extensions = set()
            for e in entries:
                extensions.add(e["info"]["extension"].lower())

            all_outputs = set()
            for ext in extensions:
                all_outputs.update(ConverterRegistry.get_valid_outputs(ext))

            if entries[0]["valid_outputs"]:
                all_outputs = set(entries[0]["valid_outputs"])
                for e in entries[1:]:
                    all_outputs = all_outputs.intersection(set(e["valid_outputs"]))

            outputs = sorted(all_outputs) if all_outputs else sorted(
                set().union(*(set(e["valid_outputs"]) for e in entries))
            )

            if not outputs:
                outputs = entries[0]["valid_outputs"]

            var = ctk.StringVar(value=outputs[0] if outputs else "")
            self._format_vars[cat_key] = var

            row = ctk.CTkFrame(self._format_section, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)

            menu = ctk.CTkOptionMenu(
                row, variable=var, values=[o.upper() for o in outputs],
                font=FONTS["body"], width=140, height=28,
                fg_color=COLORS["bg_panel"], button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                dropdown_fg_color=COLORS["bg_panel"]
            )
            menu.pack(side="left")

            count_label = ctk.CTkLabel(
                row, text=f"{len(entries)} archivo{'s' if len(entries) != 1 else ''}",
                font=FONTS["small"], text_color=COLORS["fg_muted"]
            )
            count_label.pack(side="right", padx=4)

        self._quality_options = ["Sin ajustes"]
        has_audio = FileCategory.AUDIO.value in categories_seen
        has_image = FileCategory.IMAGE.value in categories_seen
        has_video = FileCategory.VIDEO.value in categories_seen

        if has_audio:
            self._quality_options = ["Baja (64kbps)", "Normal (128kbps)", "Buena (192kbps)", "Alta (256kbps)", "Maxima (320kbps)"]
            self._quality_var.set("Buena (192kbps)")
        elif has_video:
            self._quality_options = ["Baja (480p)", "Media (720p)", "Alta (1080p)", "Ultra (2160p/4K)"]
            self._quality_var.set("Media (720p)")
        elif has_image:
            self._quality_options = ["Baja (50%)", "Media (75%)", "Alta (90%)", "Maxima (100%)"]
            self._quality_var.set("Alta (90%)")
        else:
            self._quality_var.set("Sin ajustes")

        self._quality_menu.configure(values=self._quality_options)

        self._format_section.pack(fill="x", padx=0, pady=(0, 6))
        self._quality_section.pack(fill="x", padx=0, pady=(0, 6))
        self._output_section.pack(fill="x", padx=0, pady=(0, 6))

        total = len(file_entries)
        cats = ", ".join(f"{get_category_label(FileCategory(k))} ({len(v)})" for k, v in categories_seen.items())
        self._summary_label.configure(text=f"Total: {total} archivos\nCategorias: {cats}")
        self._summary_frame.pack(fill="x", padx=0, pady=(0, 6))

        self._convert_btn.configure(state="normal")

    def _trigger_convert(self):
        if not self._on_convert or not self._file_entries:
            return

        output_dir = None if self._same_as_source.get() else self._output_dir.get()

        conversion_plan = []
        for entry in self._file_entries:
            cat = entry["info"]["category"].value
            fmt_var = self._format_vars.get(cat)
            target_format = fmt_var.get().lower() if fmt_var else entry["valid_outputs"][0]

            options = ConversionOptions(
                output_format=target_format,
                quality=self._quality_var.get() if self._quality_var.get() != "Sin ajustes" else None,
                output_dir=output_dir,
            )
            conversion_plan.append({
                "entry": entry,
                "options": options,
            })

        self._on_convert(conversion_plan)

    def set_converting(self, is_converting: bool):
        if is_converting:
            self._convert_btn.configure(
                text="CONVERTIENDO...", state="disabled",
                fg_color=COLORS["warning"], text_color="#000000", text_color_disabled="#000000"
            )
        else:
            self._convert_btn.configure(
                text="CONVERTIR", state="normal",
                fg_color=COLORS["accent"], text_color="#000000", text_color_disabled="#000000"
            )
