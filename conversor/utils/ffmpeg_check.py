import shutil
import subprocess
import os
from pathlib import Path
from ..utils.logger import logger


def check_ffmpeg() -> bool:
    """Verificar si FFmpeg está disponible en el sistema."""
    path_env = os.environ.get("PATH", "")
    logger.debug(f"PATH del sistema: {path_env}")

    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
        logger.debug("Cache de shutil.which limpiado")

    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path:
        logger.info(f"FFmpeg encontrado en: {ffmpeg_path}")
        version = check_ffmpeg_version()
        if version:
            logger.info(f"Versión de FFmpeg: {version}")
        else:
            logger.warning("FFmpeg encontrado pero no se pudo obtener la versión")
        return True
    else:
        logger.warning("FFmpeg NO encontrado en PATH")
        logger.warning("Posibles causas:")
        logger.warning("  1. FFmpeg no está instalado en el sistema")
        logger.warning("  2. FFmpeg está instalado pero no está en PATH")
        logger.warning("  3. El PATH del sistema no incluye la carpeta de FFmpeg")
        logger.warning(f"  4. La app se ejecutó antes de que FFmpeg se agregara al PATH")
        logger.warning("Solución: Reiniciar la aplicación después de instalar FFmpeg")
        return False


def check_ffmpeg_version() -> str | None:
    """Obtener la versión de FFmpeg instalada."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            first_line = result.stdout.split("\n")[0]
            return first_line.strip()
        else:
            stderr = result.stderr.strip() if result.stderr else "sin error"
            logger.debug(f"ffmpeg -version retornó código {result.returncode}: {stderr}")
    except FileNotFoundError:
        logger.debug("ffmpeg no encontrado al ejecutar -version")
    except subprocess.TimeoutExpired:
        logger.warning("Timeout al ejecutar ffmpeg -version")
    except Exception as e:
        logger.debug(f"Error al obtener versión de FFmpeg: {e}")
    return None


def get_ffmpeg_path() -> str | None:
    """Obtener la ruta completa de FFmpeg."""
    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
    path = shutil.which("ffmpeg")
    if path:
        logger.debug(f"get_ffmpeg_path: {path}")
    return path


def check_ffprobe() -> bool:
    """Verificar si FFprobe está disponible."""
    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        logger.debug(f"FFprobe encontrado en: {ffprobe_path}")
        return True
    else:
        logger.debug("FFprobe NO encontrado")
        return False
