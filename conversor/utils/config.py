import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class UserConfig:
    default_image_quality: str = "Alta (90%)"
    default_audio_quality: str = "Buena (192kbps)"
    default_video_quality: str = "Media (720p)"
    default_output_dir: str = ""
    use_same_output_dir: bool = True
    auto_delete_source: bool = False
    preserve_metadata: bool = True
    max_retries: int = 2
    max_workers: int = 3
    enable_ocr: bool = False
    ocr_language: str = "es"
    create_zip_on_batch: bool = False
    theme: str = "light"
    last_used_dir: str = ""
    show_preview: bool = True
    language: str = "es"


@dataclass
class ConversionRecord:
    id: str
    source_path: str
    output_path: str
    source_format: str
    output_format: str
    category: str
    status: str
    timestamp: str
    duration: float
    file_size_before: int
    file_size_after: int
    error_message: str = ""


class ConfigManager:
    _instance: Optional["ConfigManager"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._config_dir = self._get_config_dir()
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self._config_dir / "config.json"
        self._history_file = self._config_dir / "history.json"
        self._config = self._load_config()
        self._history: list[ConversionRecord] = self._load_history()

    def _get_config_dir(self) -> Path:
        app_data = Path.home() / "AppData" / "Local" / "ConversorDeArchivos"
        return app_data

    def _load_config(self) -> UserConfig:
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return UserConfig(**data)
            except Exception:
                pass
        return UserConfig()

    def _load_history(self) -> list[ConversionRecord]:
        if self._history_file.exists():
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [ConversionRecord(**record) for record in data]
            except Exception:
                pass
        return []

    def save_config(self):
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self._config), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")

    def get_config(self) -> UserConfig:
        return self._config

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self.save_config()

    def add_to_history(self, record: ConversionRecord):
        self._history.insert(0, record)
        if len(self._history) > 1000:
            self._history = self._history[:1000]
        self._save_history()

    def _save_history(self):
        try:
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump([asdict(record) for record in self._history], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar historial: {e}")

    def get_history(self) -> list[ConversionRecord]:
        return self._history

    def clear_history(self):
        self._history.clear()
        self._save_history()

    def get_history_stats(self) -> dict:
        total = len(self._history)
        successful = sum(1 for r in self._history if r.status == "completed")
        failed = sum(1 for r in self._history if r.status == "failed")
        total_size_saved = sum(r.file_size_before - r.file_size_after for r in self._history if r.status == "completed")
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "total_size_saved": total_size_saved,
        }


config_manager = ConfigManager()
