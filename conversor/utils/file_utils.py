from pathlib import Path
from ..core.registry import ConverterRegistry
from ..converters.base import FileCategory


def get_file_info(file_path: Path) -> dict:
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "stem": file_path.stem,
        "extension": file_path.suffix.lstrip("."),
        "size": stat.st_size,
        "category": ConverterRegistry.get_category(file_path.suffix),
        "path": file_path,
    }


def get_category_icon(category: FileCategory) -> str:
    icons = {
        FileCategory.DOCUMENT: "\U0001F4C4",
        FileCategory.AUDIO: "\U0001F3B5",
        FileCategory.IMAGE: "\U0001F5BC",
        FileCategory.VIDEO: "\U0001F3AC",
        FileCategory.UNKNOWN: "\U0001F4C1",
    }
    return icons.get(category, "\U0001F4C1")


def get_category_label(category: FileCategory) -> str:
    labels = {
        FileCategory.DOCUMENT: "Documento",
        FileCategory.AUDIO: "Audio",
        FileCategory.IMAGE: "Imagen",
        FileCategory.VIDEO: "Video",
        FileCategory.UNKNOWN: "Desconocido",
    }
    return labels.get(category, "Desconocido")


def build_file_filter() -> str:
    supported = ConverterRegistry.get_supported_extensions()
    filters = ["Todos los archivos soportados"]
    all_exts = []

    for cat, exts in supported.items():
        label = get_category_label(cat)
        ext_str = " ".join(f"*.{e}" for e in exts)
        filters.append(f"{label} ({ext_str})")
        all_exts.extend(exts)

    all_str = " ".join(f"*.{e}" for e in all_exts)
    filters[0] = f"Todos los archivos soportados ({all_str})"
    filters.append("Todos los archivos (*.*)")

    return ";;".join(filters)


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
