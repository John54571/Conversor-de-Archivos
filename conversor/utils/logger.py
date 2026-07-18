import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ConversionLogger:
    _instance: Optional["ConversionLogger"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._log_dir = self._get_log_dir()
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._current_log_file = self._get_log_file()
        self._setup_logger()

    def _get_log_dir(self) -> Path:
        app_data = Path.home() / "AppData" / "Local" / "ConversorDeArchivos"
        log_dir = app_data / "logs"
        return log_dir

    def _get_log_file(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._log_dir / f"conversor_{timestamp}.log"

    def _setup_logger(self):
        self.logger = logging.getLogger("conversor")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        file_handler = logging.FileHandler(self._current_log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def log_conversion_start(self, source: Path, target_format: str):
        self.info(f"Iniciando conversión: {source.name} -> {target_format}")

    def log_conversion_success(self, source: Path, output: Path, duration: float):
        self.info(f"Conversión exitosa: {source.name} -> {output.name} ({duration:.2f}s)")

    def log_conversion_error(self, source: Path, error: str, attempt: int = 1):
        self.error(f"Error en conversión de {source.name} (intento {attempt}): {error}")

    def log_retry(self, source: Path, attempt: int, max_attempts: int):
        self.warning(f"Reintentando conversión de {source.name} (intento {attempt}/{max_attempts})")

    def get_log_dir(self) -> Path:
        return self._log_dir

    def get_log_files(self) -> list[Path]:
        return sorted(self._log_dir.glob("conversor_*.log"), reverse=True)

    def read_log(self, log_file: Path, lines: int = 100) -> str:
        if not log_file.exists():
            return "Archivo de log no encontrado"
        
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.readlines()
            return "".join(content[-lines:])

    def get_current_log_path(self) -> Path:
        return self._current_log_file


logger = ConversionLogger()
