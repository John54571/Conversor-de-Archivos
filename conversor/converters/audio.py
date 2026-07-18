from pathlib import Path

from .base import BaseConverter, ConversionTask, FileCategory
from ..core.registry import ConverterRegistry
from ..utils.config import config_manager
from ..utils.logger import logger


@ConverterRegistry.register
class AudioConverter(BaseConverter):
    SUPPORTED_INPUT = ["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a", "opus", "aiff", "aif"]
    SUPPORTED_OUTPUT = ["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a", "opus", "aiff"]
    CATEGORY = FileCategory.AUDIO

    def get_bitrate_options(self) -> list[str]:
        return ["64 kbps", "96 kbps", "128 kbps", "192 kbps", "256 kbps", "320 kbps"]

    def get_quality_options(self) -> list[str]:
        return ["Baja (64kbps)", "Normal (128kbps)", "Buena (192kbps)", "Alta (256kbps)", "Maxima (320kbps)"]

    def _bitrate_from_quality(self, quality: str | None) -> str:
        if not quality:
            quality = config_manager.get_config().default_audio_quality
        if "64" in quality:
            return "64k"
        elif "128" in quality:
            return "128k"
        elif "192" in quality:
            return "192k"
        elif "256" in quality:
            return "256k"
        elif "320" in quality:
            return "320k"
        return "192k"

    def _extract_audio_metadata(self, src: Path) -> dict:
        metadata = {}
        if not config_manager.get_config().preserve_metadata:
            return metadata

        try:
            from mutagen.File import File as MutagenFile
            audio = MutagenFile(str(src))
            if audio and audio.tags:
                metadata["tags"] = audio.tags
                metadata["info"] = audio.info
                logger.debug(f"Metadatos extraídos de {src.name}: {list(audio.tags.keys()) if hasattr(audio.tags, 'keys') else 'presentes'}")
        except Exception as e:
            logger.debug(f"No se pudieron extraer metadatos de audio: {e}")

        return metadata

    def _apply_audio_metadata(self, output_path: Path, metadata: dict, target_format: str):
        if not metadata or not config_manager.get_config().preserve_metadata:
            return

        try:
            from mutagen.File import File as MutagenFile
            from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TDRC
            from mutagen.mp3 import MP3
            from mutagen.mp4 import MP4
            from mutagen.oggvorbis import OggVorbis
            from mutagen.flac import FLAC

            if "tags" not in metadata:
                return

            src_tags = metadata["tags"]
            
            if target_format == "mp3":
                audio = MP3(str(output_path))
                if audio.tags is None:
                    audio.add_tags()
                
                if hasattr(src_tags, "getall"):
                    for frame in src_tags.getall("TIT2"):
                        audio.tags.add(frame)
                    for frame in src_tags.getall("TPE1"):
                        audio.tags.add(frame)
                    for frame in src_tags.getall("TALB"):
                        audio.tags.add(frame)
                    for frame in src_tags.getall("TRCK"):
                        audio.tags.add(frame)
                    for frame in src_tags.getall("TDRC"):
                        audio.tags.add(frame)
                audio.save()

            elif target_format in ("m4a", "aac", "mp4"):
                audio = MP4(str(output_path))
                if audio.tags is None:
                    audio.add_tags()
                
                if hasattr(src_tags, "\xa9nam"):
                    audio.tags["\xa9nam"] = src_tags["\xa9nam"]
                if hasattr(src_tags, "\xa9ART"):
                    audio.tags["\xa9ART"] = src_tags["\xa9ART"]
                if hasattr(src_tags, "\xa9alb"):
                    audio.tags["\xa9alb"] = src_tags["\xa9alb"]
                audio.save()

            elif target_format == "ogg":
                audio = OggVorbis(str(output_path))
                if hasattr(src_tags, "get"):
                    for key in ["title", "artist", "album", "tracknumber", "date"]:
                        value = src_tags.get(key)
                        if value:
                            audio[key] = value
                audio.save()

            elif target_format == "flac":
                audio = FLAC(str(output_path))
                if hasattr(src_tags, "get"):
                    for key in ["title", "artist", "album", "tracknumber", "date"]:
                        value = src_tags.get(key)
                        if value:
                            audio[key] = value
                audio.save()

            logger.debug(f"Metadatos aplicados a {output_path.name}")
        except Exception as e:
            logger.warning(f"No se pudieron aplicar metadatos a {output_path.name}: {e}")

    def convert(self, task: ConversionTask) -> Path:
        from pydub import AudioSegment

        src = task.source_path
        tgt_ext = task.output_format.lower()
        output_dir = Path(task.options.output_dir or src.parent)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{src.stem}.{tgt_ext}"

        bitrate = self._bitrate_from_quality(task.options.quality)

        metadata = self._extract_audio_metadata(src)

        if task.on_progress:
            task.on_progress(0.2)

        src_ext = src.suffix.lower().lstrip(".")
        audio = AudioSegment.from_file(str(src), format=src_ext)

        if task.on_progress:
            task.on_progress(0.5)

        export_kwargs = {"format": tgt_ext}

        if tgt_ext in ("mp3", "ogg", "aac", "wma", "m4a", "opus"):
            export_kwargs["bitrate"] = bitrate
        elif tgt_ext == "wav":
            export_kwargs["parameters"] = ["-ar", "44100", "-sample_fmt", "s16"]
        elif tgt_ext in ("aiff", "aif"):
            export_kwargs["format"] = "aiff"
        elif tgt_ext == "flac":
            pass

        if task.on_progress:
            task.on_progress(0.7)

        audio.export(str(output_path), **export_kwargs)

        self._apply_audio_metadata(output_path, metadata, tgt_ext)

        if task.on_progress:
            task.on_progress(1.0)

        return output_path
