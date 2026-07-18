import os
import shutil
from pathlib import Path
from dataclasses import dataclass
from ..utils.logger import logger


@dataclass
class ValidationResult:
    valid: bool
    error_message: str = ""
    warning_message: str = ""


def validate_source_file(source: Path) -> ValidationResult:
    if not source.exists():
        return ValidationResult(False, f"Archivo origen no existe: {source}")
    
    if not source.is_file():
        return ValidationResult(False, f"No es un archivo: {source}")
    
    if source.stat().st_size == 0:
        return ValidationResult(False, f"Archivo vacío: {source}")
    
    try:
        with open(source, "rb") as f:
            f.read(1024)
    except PermissionError:
        return ValidationResult(False, f"Permiso denegado: {source}")
    except Exception as e:
        return ValidationResult(False, f"Error al leer archivo: {e}")
    
    return ValidationResult(True)


def validate_output_path(output: Path) -> ValidationResult:
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return ValidationResult(False, f"No se puede crear directorio: {e}")
    
    if output.exists():
        return ValidationResult(True, warning_message=f"El archivo ya existe y será sobrescrito: {output.name}")
    
    return ValidationResult(True)


def validate_disk_space(source: Path, estimated_output_size: int) -> ValidationResult:
    try:
        usage = shutil.disk_usage(source.parent)
        available = usage.free
        
        if available < estimated_output_size * 1.1:
            return ValidationResult(
                False,
                f"Espacio insuficiente. Disponible: {available // (1024*1024)}MB, Estimado: {estimated_output_size // (1024*1024)}MB"
            )
    except Exception:
        pass
    
    return ValidationResult(True)


def estimate_output_size(source: Path, target_format: str) -> int:
    source_size = source.stat().st_size
    source_ext = source.suffix.lower().lstrip(".")
    target_ext = target_format.lower()
    
    ratios = {
        ("jpg", "png"): 1.5,
        ("png", "jpg"): 0.3,
        ("bmp", "jpg"): 0.1,
        ("bmp", "png"): 0.2,
        ("wav", "mp3"): 0.1,
        ("mp3", "wav"): 10.0,
        ("flac", "mp3"): 0.3,
        ("avi", "mp4"): 0.8,
        ("mkv", "mp4"): 0.9,
    }
    
    ratio = ratios.get((source_ext, target_ext), 1.0)
    return int(source_size * ratio)


def validate_conversion(source: Path, target_format: str, output_dir: Path | None = None) -> ValidationResult:
    result = validate_source_file(source)
    if not result.valid:
        logger.error(f"Validación de origen fallida: {result.error_message}")
        return result
    
    output = output_dir / f"{source.stem}.{target_format}" if output_dir else source.parent / f"{source.stem}.{target_format}"
    result = validate_output_path(output)
    if not result.valid:
        logger.error(f"Validación de destino fallida: {result.error_message}")
        return result
    
    estimated_size = estimate_output_size(source, target_format)
    result = validate_disk_space(source, estimated_size)
    if not result.valid:
        logger.error(f"Validación de espacio fallida: {result.error_message}")
        return result
    
    if result.warning_message:
        logger.warning(result.warning_message)
    
    logger.debug(f"Validación exitosa para {source.name} -> {target_format}")
    return ValidationResult(True)
