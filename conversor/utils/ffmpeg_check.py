import shutil
import subprocess
import os
from pathlib import Path
from ..utils.logger import logger

COMMON_FFMPEG_PATHS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links",
    Path(os.environ.get("USERPROFILE", "")) / "scoop" / "shims",
    Path("C:/Program Files/ffmpeg/bin"),
    Path("C:/Program Files (x86)/ffmpeg/bin"),
    Path(os.environ.get("ProgramData", "")) / "chocolatey" / "bin",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ffmpeg" / "bin",
    Path(os.environ.get("LOCALAPPDATA", "")) / "ConversorDeArchivos" / "ffmpeg" / "bin",
]


def check_ffmpeg(configured_path: str = "") -> tuple[bool, str]:
    """Verificar si FFmpeg está disponible. Retorna (encontrado, ruta)."""
    path_env = os.environ.get("PATH", "")
    logger.debug(f"PATH del sistema: {path_env}")

    # 1. Ruta manual configurada
    if configured_path:
        logger.info(f"Usando ruta manual de FFmpeg: {configured_path}")
        ffmpeg_path = Path(configured_path)
        if ffmpeg_path.is_file() and ffmpeg_path.name.lower() == "ffmpeg.exe":
            logger.info(f"Ruta manual válida: {configured_path}")
            version = check_ffmpeg_version(str(ffmpeg_path.parent))
            if version:
                logger.info(f"Versión de FFmpeg: {version}")
            return True, str(ffmpeg_path.parent)
        elif ffmpeg_path.is_dir() and (ffmpeg_path / "ffmpeg.exe").exists():
            logger.info(f"Ruta manual válida (directorio): {configured_path}")
            version = check_ffmpeg_version(configured_path)
            if version:
                logger.info(f"Versión de FFmpeg: {version}")
            return True, configured_path
        else:
            logger.error(f"Ruta manual NO válida: {configured_path} (ffmpeg.exe no encontrado)")

    # 2. PATH del sistema
    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
        logger.debug("Cache de shutil.which limpiado")

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        logger.info(f"FFmpeg encontrado en PATH: {ffmpeg_path}")
        version = check_ffmpeg_version()
        if version:
            logger.info(f"Versión de FFmpeg: {version}")
        return True, str(Path(ffmpeg_path).parent)

    logger.warning("FFmpeg NO encontrado en PATH")

    # 3. Rutas comunes
    logger.info("Buscando FFmpeg en rutas comunes...")
    for common_path in COMMON_FFMPEG_PATHS:
        if not common_path:
            continue
        ffmpeg_exe = common_path / "ffmpeg.exe"
        if common_path.is_dir() and ffmpeg_exe.exists():
            logger.info(f"FFmpeg encontrado en ruta común: {common_path}")
            version = check_ffmpeg_version(str(common_path))
            if version:
                logger.info(f"Versión de FFmpeg: {version}")
            return True, str(common_path)
        else:
            logger.debug(f"  {common_path} → no encontrado")

    # 4. No encontrado
    logger.warning("FFmpeg NO encontrado en ninguna ubicación")
    logger.warning("Posibles causas:")
    logger.warning("  1. FFmpeg no está instalado en el sistema")
    logger.warning("  2. FFmpeg está instalado pero no está en PATH")
    logger.warning("  3. El PATH del sistema no incluye la carpeta de FFmpeg")
    logger.warning("  4. La app se ejecutó antes de que FFmpeg se agregara al PATH")
    logger.warning("Solución: Configurar la ruta de FFmpeg en Ajustes o reiniciar la aplicación")
    return False, ""


def check_ffmpeg_version(ffmpeg_dir: str = "") -> str | None:
    """Obtener la versión de FFmpeg instalada."""
    try:
        cmd = ["ffmpeg", "-version"]
        if ffmpeg_dir:
            cmd[0] = str(Path(ffmpeg_dir) / "ffmpeg.exe")

        result = subprocess.run(
            cmd,
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


def get_ffmpeg_path(configured_path: str = "") -> str | None:
    """Obtener la ruta completa de FFmpeg."""
    found, path = check_ffmpeg(configured_path)
    if found:
        logger.debug(f"get_ffmpeg_path: {path}")
        return path
    return None


def check_ffprobe(configured_path: str = "") -> bool:
    """Verificar si FFprobe está disponible."""
    if configured_path:
        ffprobe_exe = Path(configured_path) / "ffprobe.exe"
        if ffprobe_exe.exists():
            logger.debug(f"FFprobe encontrado en ruta configurada: {ffprobe_exe}")
            return True

    if hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        logger.debug(f"FFprobe encontrado en PATH: {ffprobe_path}")
        return True

    # Rutas comunes
    for common_path in COMMON_FFMPEG_PATHS:
        if not common_path:
            continue
        ffprobe_exe = common_path / "ffprobe.exe"
        if common_path.is_dir() and ffprobe_exe.exists():
            logger.debug(f"FFprobe encontrado en ruta común: {common_path}")
            return True

    logger.debug("FFprobe NO encontrado")
    return False
