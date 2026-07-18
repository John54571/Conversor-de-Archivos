from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Callable


class ConversionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileCategory(Enum):
    DOCUMENT = "document"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class ConversionOptions:
    output_format: str
    quality: Optional[str] = None
    bitrate: Optional[str] = None
    resolution: Optional[tuple] = None
    output_dir: Optional[str] = None
    extra: dict = field(default_factory=dict)


@dataclass
class ConversionTask:
    id: str
    source_path: Path
    output_format: str
    category: FileCategory
    options: ConversionOptions
    status: ConversionStatus = ConversionStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    output_path: Optional[Path] = None
    on_progress: Optional[Callable] = None
    on_complete: Optional[Callable] = None


class BaseConverter(ABC):
    SUPPORTED_INPUT: list[str] = []
    SUPPORTED_OUTPUT: list[str] = []
    CATEGORY: FileCategory = FileCategory.UNKNOWN

    @classmethod
    def can_convert(cls, source_ext: str, target_ext: str) -> bool:
        return (source_ext.lower().lstrip(".") in cls.SUPPORTED_INPUT and
                target_ext.lower().lstrip(".") in cls.SUPPORTED_OUTPUT)

    @classmethod
    def get_valid_outputs(cls, source_ext: str) -> list[str]:
        ext = source_ext.lower().lstrip(".")
        if ext in cls.SUPPORTED_INPUT:
            return [fmt for fmt in cls.SUPPORTED_OUTPUT if fmt != ext]
        return []

    @abstractmethod
    def convert(self, task: ConversionTask) -> Path:
        pass

    def get_quality_options(self) -> list[str]:
        return []

    def get_bitrate_options(self) -> list[str]:
        return []

    def get_resolution_options(self) -> list[tuple[int, int]]:
        return []
