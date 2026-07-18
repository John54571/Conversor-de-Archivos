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
        try:
            if os.path.isfile(configured_path) and configured_path.lower().endswith("ffmpeg.exe"):
                logger.info(f"Ruta manual válida: {configured_path}")
                ffmpeg_dir = str(Path(configured_path).parent)
                version = check_ffmpeg_version(ffmpeg_dir)
                if version:
                    logger.info(f"Versión de FFmpeg: {version}")
                return True, ffmpeg_dir
            elif os.path.isdir(configured_path) and os.path.isfile(os.path.join(configured_path, "ffmpeg.exe")):
                logger.info(f"Ruta manual válida (directorio): {configured_path}")
                version = check_ffmpeg_version(configured_path)
                if version:
                    logger.info(f"Versión de FFmpeg: {version}")
                return True, configured_path
            else:
                logger.error(f"Ruta manual NO válida: {configured_path} (ffmpeg.exe no encontrado)")
        except OSError as e:
            logger.error(f"Error al verificar ruta manual: {e}")

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
        try:
            common_str = str(common_path)
            ffmpeg_exe = os.path.join(common_str, "ffmpeg.exe")
            if os.path.isdir(common_str) and os.path.isfile(ffmpeg_exe):
                logger.info(f"FFmpeg encontrado en ruta común: {common_str}")
                version = check_ffmpeg_version(common_str)
                if version:
                    logger.info(f"Versión de FFmpeg: {version}")
                return True, common_str
            else:
                logger.debug(f"  {common_str} → no encontrado")
        except OSError as e:
            logger.debug(f"  {common_path} → error de acceso (reparse point): {e}")

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
            cmd[0] = os.path.join(ffmpeg_dir, "ffmpeg.exe")

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
        try:
            ffprobe_exe = os.path.join(configured_path, "ffprobe.exe")
            if os.path.isfile(ffprobe_exe):
                logger.debug(f"FFprobe encontrado en ruta configurada: {ffprobe_exe}")
                return True
        except OSError:
            pass

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
        try:
            common_str = str(common_path)
            ffprobe_exe = os.path.join(common_str, "ffprobe.exe")
            if os.path.isdir(common_str) and os.path.isfile(ffprobe_exe):
                logger.debug(f"FFprobe encontrado en ruta común: {common_str}")
                return True
        except OSError:
            logger.debug(f"  {common_path} → error de acceso (reparse point)")

    logger.debug("FFprobe NO encontrado")
    return False
