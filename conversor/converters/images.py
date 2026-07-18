from pathlib import Path

from .base import BaseConverter, ConversionTask, FileCategory
from ..core.registry import ConverterRegistry
from ..utils.config import config_manager
from ..utils.logger import logger


@ConverterRegistry.register
class ImageConverter(BaseConverter):
    SUPPORTED_INPUT = ["jpg", "jpeg", "png", "bmp", "gif", "tiff", "tif", "webp", "ico", "heic", "heif", "svg"]
    SUPPORTED_OUTPUT = ["jpg", "png", "bmp", "gif", "tiff", "webp", "ico", "pdf", "heic"]
    CATEGORY = FileCategory.IMAGE

    def get_quality_options(self) -> list[str]:
        return ["Baja (50%)", "Media (75%)", "Alta (90%)", "Maxima (100%)"]

    def _quality_to_value(self, quality: str | None) -> int:
        if not quality:
            quality = config_manager.get_config().default_image_quality
        if "50" in quality:
            return 50
        elif "75" in quality:
            return 75
        elif "90" in quality:
            return 90
        elif "100" in quality:
            return 100
        return 90

    def _extract_metadata(self, img):
        metadata = {}
        try:
            if hasattr(img, "info"):
                if "exif" in img.info:
                    metadata["exif"] = img.info["exif"]
                if "icc_profile" in img.info:
                    metadata["icc_profile"] = img.info["icc_profile"]
                if "dpi" in img.info:
                    metadata["dpi"] = img.info["dpi"]
        except Exception as e:
            logger.debug(f"No se pudieron extraer metadatos: {e}")
        return metadata

    def _apply_metadata(self, img, metadata: dict, save_kwargs: dict):
        if not config_manager.get_config().preserve_metadata:
            return

        if "exif" in metadata and metadata["exif"]:
            save_kwargs["exif"] = metadata["exif"]
        if "icc_profile" in metadata and metadata["icc_profile"]:
            save_kwargs["icc_profile"] = metadata["icc_profile"]
        if "dpi" in metadata and metadata["dpi"]:
            save_kwargs["dpi"] = metadata["dpi"]

    def convert(self, task: ConversionTask) -> Path:
        from PIL import Image

        src = task.source_path
        tgt_ext = task.output_format.lower()
        output_dir = Path(task.options.output_dir or src.parent)
        output_dir.mkdir(parents=True, exist_ok=True)

        if tgt_ext in ("jpg", "jpeg"):
            output_path = output_dir / f"{src.stem}.jpg"
        elif tgt_ext == "tiff":
            output_path = output_dir / f"{src.stem}.tiff"
        else:
            output_path = output_dir / f"{src.stem}.{tgt_ext}"

        quality = self._quality_to_value(task.options.quality)

        src_ext = src.suffix.lower().lstrip(".")

        if src_ext in ("heic", "heif"):
            try:
                from pillow_heif import register_heif_opener
                register_heif_opener()
            except ImportError:
                logger.warning("pillow-heif no disponible, intentando conversión básica")

        if src_ext == "svg":
            return self._convert_svg(src, output_path, tgt_ext, quality, task)

        img = Image.open(str(src))
        metadata = self._extract_metadata(img)

        if task.on_progress:
            task.on_progress(0.3)

        if tgt_ext in ("jpg", "jpeg") and img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif tgt_ext == "ico":
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            img.save(str(output_path), format="ICO", sizes=sizes)
            if task.on_progress:
                task.on_progress(1.0)
            return output_path
        elif tgt_ext == "pdf":
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(str(output_path), format="PDF", resolution=150)
            if task.on_progress:
                task.on_progress(1.0)
            return output_path

        save_kwargs = {}
        if tgt_ext in ("jpg", "jpeg", "webp"):
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif tgt_ext == "png":
            save_kwargs["optimize"] = True

        self._apply_metadata(img, metadata, save_kwargs)

        if img.mode == "RGBA" and tgt_ext in ("jpg", "jpeg", "bmp"):
            img = img.convert("RGB")

        fmt_map = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "bmp": "BMP",
            "gif": "GIF",
            "tiff": "TIFF",
            "tif": "TIFF",
            "webp": "WEBP",
            "heic": "HEIF",
        }

        if task.on_progress:
            task.on_progress(0.6)

        img.save(str(output_path), format=fmt_map.get(tgt_ext, tgt_ext.upper()), **save_kwargs)

        if task.on_progress:
            task.on_progress(1.0)

        return output_path

    def _convert_svg(self, src: Path, output_path: Path, tgt_ext: str, quality: int, task: ConversionTask) -> Path:
        try:
            import cairosvg
            
            if tgt_ext == "png":
                cairosvg.svg2png(url=str(src), write_path=str(output_path))
            elif tgt_ext in ("jpg", "jpeg"):
                from PIL import Image
                import io
                png_data = cairosvg.svg2png(url=str(src))
                img = Image.open(io.BytesIO(png_data))
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(str(output_path), format="JPEG", quality=quality)
            elif tgt_ext == "pdf":
                cairosvg.svg2pdf(url=str(src), write_path=str(output_path))
            else:
                cairosvg.svg2png(url=str(src), write_path=str(output_path))

            if task.on_progress:
                task.on_progress(1.0)
            return output_path
        except ImportError:
            raise ValueError("cairosvg no está instalado. Instálalo con: uv add cairosvg")
        except Exception as e:
            raise ValueError(f"Error al convertir SVG: {e}")
