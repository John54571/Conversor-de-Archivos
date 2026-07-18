import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk
from .themes import COLORS, FONTS, SIZES
from ..utils.file_utils import get_file_info, get_category_label, format_file_size
from ..converters.base import FileCategory


class PreviewPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_panel"], corner_radius=SIZES["border_radius"], **kwargs)
        
        self._current_file: Path | None = None
        self._photo_image = None
        self._audio_player = None
        self._video_player = None
        
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_header"], corner_radius=0, height=40)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header, text="  Vista previa", font=FONTS["heading"],
            text_color=COLORS["fg_header"], anchor="w"
        )
        title.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._content_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self._empty_label = ctk.CTkLabel(
            self._content_frame, text="Selecciona un archivo\npara ver la vista previa",
            font=FONTS["body"], text_color=COLORS["fg_muted"]
        )
        self._empty_label.pack(expand=True)

        self._info_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_group"], corner_radius=4)
        self._info_frame.pack(fill="x", padx=6, pady=(0, 6))

        self._info_label = ctk.CTkLabel(
            self._info_frame, text="", font=FONTS["small"],
            text_color=COLORS["fg_secondary"], justify="left"
        )
        self._info_label.pack(fill="x", padx=8, pady=6)

    def show_preview(self, file_path: Path):
        self._clear_preview()
        self._current_file = file_path
        
        if not file_path.exists():
            return

        info = get_file_info(file_path)
        category = info["category"]
        
        info_text = f"Archivo: {file_path.name}\n"
        info_text += f"Tipo: {get_category_label(category)}\n"
        info_text += f"Formato: {info['extension'].upper()}\n"
        info_text += f"Tamaño: {format_file_size(info['size'])}"
        
        self._info_label.configure(text=info_text)

        if category == FileCategory.IMAGE:
            self._show_image_preview(file_path)
        elif category == FileCategory.AUDIO:
            self._show_audio_preview(file_path)
        elif category == FileCategory.VIDEO:
            self._show_video_preview(file_path)
        else:
            self._show_document_preview(file_path)

    def _show_image_preview(self, file_path: Path):
        try:
            img = Image.open(str(file_path))
            
            max_width = 280
            max_height = 200
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            self._photo_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            image_label = ctk.CTkLabel(self._content_frame, image=self._photo_image, text="")
            image_label.pack(expand=True, padx=10, pady=10)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self._content_frame, text=f"No se pudo cargar la imagen:\n{str(e)[:50]}",
                font=FONTS["small"], text_color=COLORS["error"]
            )
            error_label.pack(expand=True)

    def _show_audio_preview(self, file_path: Path):
        try:
            from mutagen.File import File as MutagenFile
            
            audio = MutagenFile(str(file_path))
            info_text = f"Duración: {self._format_duration(audio.info.length) if audio and audio.info else 'N/A'}\n"
            
            if audio and audio.info:
                if hasattr(audio.info, "bitrate"):
                    info_text += f"Bitrate: {audio.info.bitrate // 1000} kbps\n"
                if hasattr(audio.info, "sample_rate"):
                    info_text += f"Sample rate: {audio.info.sample_rate} Hz\n"
                if hasattr(audio.info, "channels"):
                    info_text += f"Canales: {audio.info.channels}"
            
            info_label = ctk.CTkLabel(
                self._content_frame, text=f"Archivo de audio\n\n{info_text}",
                font=FONTS["body"], text_color=COLORS["fg_primary"], justify="center"
            )
            info_label.pack(expand=True, padx=20, pady=20)

            controls_frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
            controls_frame.pack(fill="x", padx=20, pady=10)

            play_btn = ctk.CTkButton(
                controls_frame, text="Reproducir", width=100,
                font=FONTS["body"], fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                command=lambda: self._play_audio(file_path)
            )
            play_btn.pack(side="left", expand=True, padx=5)

            stop_btn = ctk.CTkButton(
                controls_frame, text="Detener", width=100,
                font=FONTS["body"], fg_color=COLORS["button_bg"],
                hover_color=COLORS["button_hover"],
                command=self._stop_audio
            )
            stop_btn.pack(side="right", expand=True, padx=5)

        except Exception as e:
            error_label = ctk.CTkLabel(
                self._content_frame, text=f"No se pudo cargar información de audio:\n{str(e)[:50]}",
                font=FONTS["small"], text_color=COLORS["error"]
            )
            error_label.pack(expand=True)

    def _show_video_preview(self, file_path: Path):
        info_label = ctk.CTkLabel(
            self._content_frame, text=f"Archivo de video\n\n{file_path.name}",
            font=FONTS["body"], text_color=COLORS["fg_primary"], justify="center"
        )
        info_label.pack(expand=True, padx=20, pady=20)

        controls_frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=10)

        play_btn = ctk.CTkButton(
            controls_frame, text="Reproducir", width=100,
            font=FONTS["body"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=lambda: self._play_video(file_path)
        )
        play_btn.pack(side="left", expand=True, padx=5)

        stop_btn = ctk.CTkButton(
            controls_frame, text="Detener", width=100,
            font=FONTS["body"], fg_color=COLORS["button_bg"],
            hover_color=COLORS["button_hover"],
            command=self._stop_video
        )
        stop_btn.pack(side="right", expand=True, padx=5)

    def _show_document_preview(self, file_path: Path):
        info_label = ctk.CTkLabel(
            self._content_frame, text=f"Archivo de documento\n\n{file_path.name}\n\nVista previa no disponible",
            font=FONTS["body"], text_color=COLORS["fg_primary"], justify="center"
        )
        info_label.pack(expand=True, padx=20, pady=20)

    def _play_audio(self, file_path: Path):
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.play()
            self._audio_player = pygame
        except Exception as e:
            print(f"Error al reproducir audio: {e}")

    def _stop_audio(self):
        try:
            if self._audio_player:
                self._audio_player.mixer.music.stop()
        except Exception:
            pass

    def _play_video(self, file_path: Path):
        import subprocess
        import sys
        
        if sys.platform == "win32":
            os.startfile(str(file_path))
        else:
            subprocess.run(["xdg-open", str(file_path)])

    def _stop_video(self):
        pass

    def _format_duration(self, seconds: float) -> str:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def _clear_preview(self):
        for widget in self._content_frame.winfo_children():
            widget.destroy()
        
        self._stop_audio()
        self._photo_image = None
        self._audio_player = None
        self._video_player = None

    def clear(self):
        self._clear_preview()
        self._empty_label.pack(expand=True)
        self._info_label.configure(text="")
