from pathlib import Path
from .registry import ConverterRegistry
from ..converters.base import FileCategory


def get_file_category(file_path: Path) -> FileCategory:
    return ConverterRegistry.get_category(file_path.suffix)


def get_valid_output_formats(file_path: Path) -> list[str]:
    return ConverterRegistry.get_valid_outputs(file_path.suffix)


def validate_conversion(source: Path, target_format: str) -> bool:
    converter = ConverterRegistry.get_converter(source.suffix, target_format)
    return converter is not None


def get_output_path(source: Path, target_format: str, output_dir: Path | None = None) -> Path:
    directory = output_dir or source.parent
    return directory / f"{source.stem}.{target_format}"


def is_supported_file(file_path: Path) -> bool:
    category = get_file_category(file_path)
    return category != FileCategory.UNKNOWN


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
