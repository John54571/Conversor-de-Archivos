import customtkinter as ctk
from typing import Callable

from .themes import COLORS, FONTS, SIZES
from ..converters.base import ConversionTask, ConversionStatus
from ..utils.file_utils import get_category_icon, format_file_size


class ProgressPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_panel"], corner_radius=SIZES["border_radius"], **kwargs)

        self._task_widgets: dict[str, dict] = {}
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_header"], corner_radius=0, height=40)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        self._title_label = ctk.CTkLabel(
            header, text="  Progreso", font=FONTS["heading"],
            text_color=COLORS["fg_header"], anchor="w"
        )
        self._title_label.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=4, pady=4)

        self._cancel_all_btn = ctk.CTkButton(
            btn_frame, text="Cancelar todo", width=90, height=26,
            font=FONTS["small"], fg_color="transparent",
            text_color=COLORS["fg_header"],
            hover_color=COLORS["bg_header_hover"],
            corner_radius=3, command=self._cancel_all
        )
        self._cancel_all_btn.pack(side="left", padx=2)

        self._clear_btn = ctk.CTkButton(
            btn_frame, text="Limpiar", width=60, height=26,
            font=FONTS["small"], fg_color="transparent",
            text_color=COLORS["fg_header"],
            hover_color=COLORS["bg_header_hover"],
            corner_radius=3, command=self._clear_completed
        )
        self._clear_btn.pack(side="left", padx=2)

        self._global_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_group"], corner_radius=4)
        self._global_frame.pack(fill="x", padx=6, pady=(6, 2))

        self._global_label = ctk.CTkLabel(
            self._global_frame, text="Esperando tareas...",
            font=FONTS["small"], text_color=COLORS["fg_secondary"], anchor="w"
        )
        self._global_label.pack(fill="x", padx=8, pady=(6, 0))

        self._global_progress = ctk.CTkProgressBar(
            self._global_frame, height=10,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["progress_fill"],
            corner_radius=5
        )
        self._global_progress.pack(fill="x", padx=8, pady=(2, 2))
        self._global_progress.set(0)

        self._time_label = ctk.CTkLabel(
            self._global_frame, text="Tiempo estimado: --",
            font=FONTS["small"], text_color=COLORS["fg_muted"], anchor="w"
        )
        self._time_label.pack(fill="x", padx=8, pady=(0, 6))

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=6, pady=(2, 6))

        self._on_cancel_all: Callable | None = None
        self._on_clear_completed: Callable | None = None

    def set_callbacks(self, on_cancel_all: Callable, on_clear_completed: Callable):
        self._on_cancel_all = on_cancel_all
        self._on_clear_completed = on_clear_completed

    def _cancel_all(self):
        if self._on_cancel_all:
            self._on_cancel_all()

    def _clear_completed(self):
        if self._on_clear_completed:
            self._on_clear_completed()
        for task_id, widgets in list(self._task_widgets.items()):
            widgets["frame"].destroy()
            del self._task_widgets[task_id]

    def add_task(self, task: ConversionTask):
        if task.id in self._task_widgets:
            return

        row = ctk.CTkFrame(self._scroll, fg_color=COLORS["bg_secondary"], corner_radius=3, height=50)
        row.pack(fill="x", padx=0, pady=1)

        icon = get_category_icon(task.category)
        icon_label = ctk.CTkLabel(row, text=icon, width=24, font=("Segoe UI Emoji", 13))
        icon_label.pack(side="left", padx=(8, 4))

        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=4)

        name_label = ctk.CTkLabel(
            info_frame, text=task.source_path.name,
            font=FONTS["small"], text_color=COLORS["fg_primary"], anchor="w"
        )
        name_label.pack(fill="x", anchor="w")

        target_text = f"{task.source_path.suffix.lstrip('.').upper()} -> {task.output_format.upper()}"
        format_label = ctk.CTkLabel(
            info_frame, text=target_text,
            font=FONTS["small"], text_color=COLORS["fg_muted"], anchor="w"
        )
        format_label.pack(fill="x", anchor="w")

        progress = ctk.CTkProgressBar(
            info_frame, height=6,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["progress_fill"],
            corner_radius=3
        )
        progress.pack(fill="x", pady=(2, 4))
        progress.set(0)

        status_label = ctk.CTkLabel(
            row, text="En cola", font=FONTS["small"],
            text_color=COLORS["fg_muted"], width=70
        )
        status_label.pack(side="right", padx=8)

        self._task_widgets[task.id] = {
            "frame": row,
            "name_label": name_label,
            "format_label": format_label,
            "progress": progress,
            "status_label": status_label,
        }

    def update_task(self, task: ConversionTask):
        widgets = self._task_widgets.get(task.id)
        if not widgets:
            self.add_task(task)
            widgets = self._task_widgets.get(task.id)
            if not widgets:
                return

        widgets["progress"].set(task.progress)

        status_map = {
            ConversionStatus.PENDING: ("En cola", COLORS["fg_muted"]),
            ConversionStatus.IN_PROGRESS: (f"{int(task.progress * 100)}%", COLORS["accent"]),
            ConversionStatus.COMPLETED: ("Completado", COLORS["success"]),
            ConversionStatus.FAILED: ("Error", COLORS["error"]),
            ConversionStatus.CANCELLED: ("Cancelado", COLORS["warning"]),
        }

        text, color = status_map.get(task.status, ("?", COLORS["fg_muted"]))
        widgets["status_label"].configure(text=text, text_color=color)

        if task.status == ConversionStatus.IN_PROGRESS:
            widgets["progress"].configure(progress_color=COLORS["progress_fill"])
        elif task.status == ConversionStatus.COMPLETED:
            widgets["progress"].configure(progress_color=COLORS["success"])
        elif task.status == ConversionStatus.FAILED:
            widgets["progress"].configure(progress_color=COLORS["error"])
            if task.error_message:
                widgets["format_label"].configure(text=task.error_message[:40], text_color=COLORS["error"])

    def update_global(self, summary: dict, estimated_time: float = 0.0):
        total = summary["total"]
        completed = summary["completed"]
        failed = summary["failed"]
        in_progress = summary["in_progress"]

        if total == 0:
            self._global_label.configure(text="Esperando tareas...")
            self._global_progress.set(0)
            self._time_label.configure(text="Tiempo estimado: --")
            return

        done = completed + failed
        pct = done / total if total > 0 else 0
        self._global_progress.set(pct)

        parts = []
        if completed:
            parts.append(f"{completed} completado{'s' if completed != 1 else ''}")
        if in_progress:
            parts.append(f"{in_progress} en progreso")
        if failed:
            parts.append(f"{failed} error{'es' if failed != 1 else ''}")

        pending = total - done - in_progress
        if pending > 0:
            parts.append(f"{pending} en cola")

        self._global_label.configure(text=f"{done}/{total} - {', '.join(parts)}")

        if estimated_time > 0:
            minutes = int(estimated_time // 60)
            seconds = int(estimated_time % 60)
            if minutes > 0:
                time_text = f"Tiempo estimado: {minutes}m {seconds}s"
            else:
                time_text = f"Tiempo estimado: {seconds}s"
        else:
            time_text = "Tiempo estimado: --"
        
        self._time_label.configure(text=time_text)

    def clear_all(self):
        for widgets in self._task_widgets.values():
            widgets["frame"].destroy()
        self._task_widgets.clear()
        self._global_label.configure(text="Esperando tareas...")
        self._global_progress.set(0)
        self._time_label.configure(text="Tiempo estimado: --")
