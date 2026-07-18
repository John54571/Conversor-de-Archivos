from pathlib import Path

from .base import BaseConverter, ConversionTask, FileCategory
from ..core.registry import ConverterRegistry
from ..utils.config import config_manager
from ..utils.logger import logger


@ConverterRegistry.register
class VideoConverter(BaseConverter):
    SUPPORTED_INPUT = ["mp4", "avi", "mkv", "mov", "webm", "flv", "wmv", "m4v", "mpg", "mpeg", "3gp", "ts"]
    SUPPORTED_OUTPUT = ["mp4", "avi", "mkv", "mov", "webm", "gif", "3gp"]
    CATEGORY = FileCategory.VIDEO

    def get_quality_options(self) -> list[str]:
        return ["Baja (480p)", "Media (720p)", "Alta (1080p)", "Ultra (2160p/4K)"]

    def get_resolution_options(self) -> list[tuple[int, int]]:
        return [(858, 480), (1280, 720), (1920, 1080), (3840, 2160)]

    def _resolution_from_quality(self, quality: str | None) -> str | None:
        if not quality:
            quality = config_manager.get_config().default_video_quality
        if "480" in quality:
            return "858:480"
        elif "720" in quality:
            return "1280:720"
        elif "1080" in quality:
            return "1920:1080"
        elif "2160" in quality or "4K" in quality:
            return "3840:2160"
        return None

    def convert(self, task: ConversionTask) -> Path:
        import ffmpeg
        from pathlib import Path as P

        src = task.source_path
        tgt_ext = task.output_format.lower()
        output_dir = Path(task.options.output_dir or src.parent)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{src.stem}.{tgt_ext}"

        resolution = self._resolution_from_quality(task.options.quality)

        if task.on_progress:
            task.on_progress(0.1)

        # Configurar ruta de FFmpeg para ffmpeg-python
        configured_path = config_manager.get_config().ffmpeg_path
        ffmpeg_cmd = "ffmpeg"
        if configured_path:
            ffmpeg_exe = P(configured_path)
            if ffmpeg_exe.is_file() and ffmpeg_exe.name.lower() == "ffmpeg.exe":
                ffmpeg_cmd = str(ffmpeg_exe)
                logger.debug(f"ffmpeg-python usando: {ffmpeg_cmd}")
            elif ffmpeg_exe.is_dir():
                ffmpeg_cmd = str(ffmpeg_exe / "ffmpeg.exe")
                logger.debug(f"ffmpeg-python usando: {ffmpeg_cmd}")

        try:
            stream = ffmpeg.input(str(src))

            if tgt_ext == "gif":
                stream = stream.filter("fps", fps=10).filter("scale", 480, -1, flags="lanczos")
                if task.on_progress:
                    task.on_progress(0.4)
                ffmpeg.output(stream, str(output_path), format="gif").overwrite_output().run(
                    cmd=ffmpeg_cmd, capture_stdout=True, capture_stderr=True
                )
            else:
                codec_map = {
                    "mp4": {"vcodec": "libx264", "acodec": "aac"},
                    "avi": {"vcodec": "mpeg4", "acodec": "mp3"},
                    "mkv": {"vcodec": "libx264", "acodec": "aac"},
                    "mov": {"vcodec": "libx264", "acodec": "aac"},
                    "webm": {"vcodec": "libvpx-vp9", "acodec": "libopus"},
                    "3gp": {"vcodec": "h263", "acodec": "aac"},
                }

                codecs = codec_map.get(tgt_ext, {"vcodec": "libx264", "acodec": "aac"})

                if resolution:
                    w, h = resolution.split(":")
                    stream = stream.filter("scale", int(w), int(h))

                if task.on_progress:
                    task.on_progress(0.4)

                output_kwargs = {
                    "vcodec": codecs["vcodec"],
                    "acodec": codecs["acodec"],
                }

                if tgt_ext in ("mp4", "mkv", "mov"):
                    output_kwargs["preset"] = "medium"
                    output_kwargs["crf"] = "23"

                output_stream = ffmpeg.output(stream, str(output_path), **output_kwargs)

                if task.on_progress:
                    task.on_progress(0.6)

                output_stream.overwrite_output().run(cmd=ffmpeg_cmd, capture_stdout=True, capture_stderr=True)

            if task.on_progress:
                task.on_progress(1.0)

            return output_path

        except ffmpeg.Error as e:
            error_msg = e.stderr.decode("utf-8") if e.stderr else str(e)
            logger.error(f"Error de FFmpeg al convertir {src.name}: {error_msg[:500]}")
            raise ValueError(f"Error de conversión de video: {error_msg[:200]}")
        except Exception as e:
            logger.error(f"Error inesperado al convertir {src.name}: {e}")
            raise
