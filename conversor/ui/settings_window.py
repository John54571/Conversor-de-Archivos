import customtkinter as ctk
import threading
from .themes import COLORS, FONTS, SIZES
from ..utils.config import config_manager, UserConfig
from ..utils.update_checker import get_current_version, check_for_updates


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ajustes")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_primary"])
        
        self._config = config_manager.get_config()
        self._build_ui()
        
        self.grab_set()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=16)

        general_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_group"], corner_radius=6)
        general_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(general_frame, text="General", font=FONTS["heading"],
                     text_color=COLORS["fg_primary"]).pack(fill="x", padx=12, pady=(10, 6))

        self._max_workers_var = ctk.StringVar(value=str(self._config.max_workers))
        workers_frame = ctk.CTkFrame(general_frame, fg_color="transparent")
        workers_frame.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(workers_frame, text="Trabajos simultaneos:", font=FONTS["body"],
                     text_color=COLORS["fg_primary"]).pack(side="left")
        workers_menu = ctk.CTkOptionMenu(workers_frame, variable=self._max_workers_var,
                                          values=["1", "2", "3", "4", "5"], width=80,
                                          font=FONTS["body"], fg_color=COLORS["bg_panel"],
                                          button_color=COLORS["accent"],
                                          button_hover_color=COLORS["accent_hover"])
        workers_menu.pack(side="right")

        self._max_retries_var = ctk.StringVar(value=str(self._config.max_retries))
        retries_frame = ctk.CTkFrame(general_frame, fg_color="transparent")
        retries_frame.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(retries_frame, text="Reintentos maximos:", font=FONTS["body"],
                     text_color=COLORS["fg_primary"]).pack(side="left")
        retries_menu = ctk.CTkOptionMenu(retries_frame, variable=self._max_retries_var,
                                          values=["0", "1", "2", "3", "5"], width=80,
                                          font=FONTS["body"], fg_color=COLORS["bg_panel"],
                                          button_color=COLORS["accent"],
                                          button_hover_color=COLORS["accent_hover"])
        retries_menu.pack(side="right")

        self._metadata_var = ctk.BooleanVar(value=self._config.preserve_metadata)
        ctk.CTkCheckBox(general_frame, text="Preservar metadatos", variable=self._metadata_var,
                        font=FONTS["body"], fg_color=COLORS["accent"],
                        hover_color=COLORS["accent_hover"]).pack(fill="x", padx=12, pady=4)

        self._preview_var = ctk.BooleanVar(value=self._config.show_preview)
        ctk.CTkCheckBox(general_frame, text="Mostrar vista previa", variable=self._preview_var,
                        font=FONTS["body"], fg_color=COLORS["accent"],
                        hover_color=COLORS["accent_hover"]).pack(fill="x", padx=12, pady=4)

        quality_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_group"], corner_radius=6)
        quality_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(quality_frame, text="Calidad por defecto", font=FONTS["heading"],
                     text_color=COLORS["fg_primary"]).pack(fill="x", padx=12, pady=(10, 6))

        self._img_quality_var = ctk.StringVar(value=self._config.default_image_quality)
        img_frame = ctk.CTkFrame(quality_frame, fg_color="transparent")
        img_frame.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(img_frame, text="Imagenes:", font=FONTS["body"],
                     text_color=COLORS["fg_primary"]).pack(side="left")
        ctk.CTkOptionMenu(img_frame, variable=self._img_quality_var,
                          values=["Baja (50%)", "Media (75%)", "Alta (90%)", "Maxima (100%)"],
                          width=160, font=FONTS["body"], fg_color=COLORS["bg_panel"],
                          button_color=COLORS["accent"],
                          button_hover_color=COLORS["accent_hover"]).pack(side="right")

        self._audio_quality_var = ctk.StringVar(value=self._config.default_audio_quality)
        audio_frame = ctk.CTkFrame(quality_frame, fg_color="transparent")
        audio_frame.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(audio_frame, text="Audio:", font=FONTS["body"],
                     text_color=COLORS["fg_primary"]).pack(side="left")
        ctk.CTkOptionMenu(audio_frame, variable=self._audio_quality_var,
                          values=["Baja (64kbps)", "Normal (128kbps)", "Buena (192kbps)",
                                  "Alta (256kbps)", "Maxima (320kbps)"],
                          width=160, font=FONTS["body"], fg_color=COLORS["bg_panel"],
                          button_color=COLORS["accent"],
                          button_hover_color=COLORS["accent_hover"]).pack(side="right")

        self._video_quality_var = ctk.StringVar(value=self._config.default_video_quality)
        video_frame = ctk.CTkFrame(quality_frame, fg_color="transparent")
        video_frame.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(video_frame, text="Video:", font=FONTS["body"],
                     text_color=COLORS["fg_primary"]).pack(side="left")
        ctk.CTkOptionMenu(video_frame, variable=self._video_quality_var,
                          values=["Baja (480p)", "Media (720p)", "Alta (1080p)", "Ultra (2160p/4K)"],
                          width=160, font=FONTS["body"], fg_color=COLORS["bg_panel"],
                          button_color=COLORS["accent"],
                          button_hover_color=COLORS["accent_hover"]).pack(side="right")

        ocr_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_group"], corner_radius=6)
        ocr_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(ocr_frame, text="OCR (Reconocimiento de texto)", font=FONTS["heading"],
                     text_color=COLORS["fg_primary"]).pack(fill="x", padx=12, pady=(10, 6))

        self._ocr_var = ctk.BooleanVar(value=self._config.enable_ocr)
        ctk.CTkCheckBox(ocr_frame, text="Usar PaddleOCR para PDF a texto",
                        variable=self._ocr_var, font=FONTS["body"],
                        fg_color=COLORS["accent"],
                        hover_color=COLORS["accent_hover"]).pack(fill="x", padx=12, pady=4)

        ocr_lang_frame = ctk.CTkFrame(ocr_frame, fg_color="transparent")
        ocr_lang_frame.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(ocr_lang_frame, text="Idioma OCR:", font=FONTS["body"],
                     text_color=COLORS["fg_primary"]).pack(side="left")
        self._ocr_lang_var = ctk.StringVar(value=self._config.ocr_language)
        ctk.CTkOptionMenu(ocr_lang_frame, variable=self._ocr_lang_var,
                          values=["es", "en", "fr", "de", "it", "pt", "zh", "ja", "ko"],
                          width=100, font=FONTS["body"], fg_color=COLORS["bg_panel"],
                          button_color=COLORS["accent"],
                          button_hover_color=COLORS["accent_hover"]).pack(side="right")

        ctk.CTkLabel(ocr_frame, text="Nota: OCR consume muchos recursos. Usar solo para PDFs escaneados.",
                     font=FONTS["small"], text_color=COLORS["warning"], wraplength=440,
                     justify="left").pack(fill="x", padx=12, pady=(4, 10))

        output_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_group"], corner_radius=6)
        output_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(output_frame, text="Salida", font=FONTS["heading"],
                     text_color=COLORS["fg_primary"]).pack(fill="x", padx=12, pady=(10, 6))

        self._zip_var = ctk.BooleanVar(value=self._config.create_zip_on_batch)
        ctk.CTkCheckBox(output_frame, text="Crear archivo ZIP al convertir multiples archivos",
                        variable=self._zip_var, font=FONTS["body"],
                        fg_color=COLORS["accent"],
                        hover_color=COLORS["accent_hover"]).pack(fill="x", padx=12, pady=4)

        self._auto_delete_var = ctk.BooleanVar(value=self._config.auto_delete_source)
        ctk.CTkCheckBox(output_frame, text="Eliminar archivos origen despues de convertir",
                        variable=self._auto_delete_var, font=FONTS["body"],
                        fg_color=COLORS["accent"],
                        hover_color=COLORS["accent_hover"]).pack(fill="x", padx=12, pady=(4, 10))

        about_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_group"], corner_radius=6)
        about_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(about_frame, text="Acerca de", font=FONTS["heading"],
                     text_color=COLORS["fg_primary"]).pack(fill="x", padx=12, pady=(10, 6))

        current_version = get_current_version()
        ctk.CTkLabel(about_frame, text=f"Version actual: {current_version}",
                     font=FONTS["body"], text_color=COLORS["fg_primary"]).pack(fill="x", padx=12, pady=4)

        self._update_status_label = ctk.CTkLabel(
            about_frame, text="", font=FONTS["small"],
            text_color=COLORS["fg_muted"]
        )
        self._update_status_label.pack(fill="x", padx=12, pady=4)

        self._check_update_btn = ctk.CTkButton(
            about_frame, text="Buscar actualizaciones", width=180, height=30,
            font=FONTS["body_bold"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], text_color=COLORS["fg_header"],
            command=self._check_for_updates_manual
        )
        self._check_update_btn.pack(fill="x", padx=12, pady=(4, 10))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(btn_frame, text="Guardar", font=FONTS["body_bold"],
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      text_color=COLORS["fg_header"], width=120,
                      command=self._save_settings).pack(side="right", padx=4)

        ctk.CTkButton(btn_frame, text="Cancelar", font=FONTS["body"],
                      fg_color=COLORS["button_bg"], hover_color=COLORS["button_hover"],
                      text_color=COLORS["fg_primary"], width=120,
                      command=self.destroy).pack(side="right", padx=4)

    def _save_settings(self):
        config_manager.update_config(
            max_workers=int(self._max_workers_var.get()),
            max_retries=int(self._max_retries_var.get()),
            preserve_metadata=self._metadata_var.get(),
            show_preview=self._preview_var.get(),
            default_image_quality=self._img_quality_var.get(),
            default_audio_quality=self._audio_quality_var.get(),
            default_video_quality=self._video_quality_var.get(),
            enable_ocr=self._ocr_var.get(),
            ocr_language=self._ocr_lang_var.get(),
            create_zip_on_batch=self._zip_var.get(),
            auto_delete_source=self._auto_delete_var.get(),
        )
        self.destroy()

    def _check_for_updates_manual(self):
        self._check_update_btn.configure(state="disabled", text="Buscando...")
        self._update_status_label.configure(text="Buscando actualizaciones...", text_color=COLORS["fg_muted"])

        def _do_check():
            release_info = check_for_updates()
            self.after(0, lambda: self._show_update_result(release_info))

        threading.Thread(target=_do_check, daemon=True).start()

    def _show_update_result(self, release_info):
        self._check_update_btn.configure(state="normal", text="Buscar actualizaciones")
        
        if release_info is None:
            self._update_status_label.configure(
                text="La aplicacion esta actualizada",
                text_color=COLORS["success"]
            )
        else:
            from .update_dialog import UpdateDialog
            self._update_status_label.configure(
                text=f"Nueva version disponible: {release_info.version}",
                text_color=COLORS["accent"]
            )
            UpdateDialog(self.winfo_toplevel(), release_info)
