import zipfile
from pathlib import Path
from typing import Callable
from ..utils.logger import logger


def create_zip_from_files(
    files: list[Path],
    output_zip: Path,
    on_progress: Callable | None = None
) -> Path:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(str(output_zip), "w", zipfile.ZIP_DEFLATED) as zipf:
        total = len(files)
        for i, file_path in enumerate(files):
            if file_path.exists() and file_path.is_file():
                zipf.write(str(file_path), file_path.name)
                logger.debug(f"Agregado al ZIP: {file_path.name}")
            
            if on_progress:
                on_progress((i + 1) / total)
    
    logger.info(f"ZIP creado: {output_zip.name} ({len(files)} archivos)")
    return output_zip


def create_zip_from_directory(
    directory: Path,
    output_zip: Path,
    pattern: str = "*",
    on_progress: Callable | None = None
) -> Path:
    files = list(directory.glob(pattern))
    return create_zip_from_files(files, output_zip, on_progress)
