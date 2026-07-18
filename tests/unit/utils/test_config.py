"""Tests for config manager."""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestUserConfig:
    """Test UserConfig dataclass."""

    def test_default_values(self):
        from conversor.utils.config import UserConfig
        config = UserConfig()
        assert config.max_workers == 3
        assert config.max_retries == 2
        assert config.preserve_metadata is True
        assert config.show_preview is True
        assert config.default_image_quality == "Alta (90%)"
        assert config.default_audio_quality == "Buena (192kbps)"
        assert config.default_video_quality == "Media (720p)"
        assert config.enable_ocr is False
        assert config.ocr_language == "es"
        assert config.create_zip_on_batch is False
        assert config.auto_delete_source is False

    def test_custom_values(self):
        from conversor.utils.config import UserConfig
        config = UserConfig(max_workers=5, max_retries=3)
        assert config.max_workers == 5
        assert config.max_retries == 3


class TestConversionRecord:
    """Test ConversionRecord dataclass."""

    def test_creation(self):
        from conversor.utils.config import ConversionRecord
        record = ConversionRecord(
            id="test1",
            source_path="test.docx",
            output_path="test.pdf",
            source_format="docx",
            output_format="pdf",
            category="document",
            status="completed",
            timestamp="2026-07-18T12:00:00",
            duration=1.5,
            file_size_before=1000,
            file_size_after=500,
        )
        assert record.source_path == "test.docx"
        assert record.output_format == "pdf"
        assert record.status == "completed"
        assert record.duration == 1.5


class TestConfigManager:
    """Test ConfigManager singleton."""

    def test_singleton_pattern(self):
        from conversor.utils.config import ConfigManager, config_manager
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        assert manager1 is manager2
        assert config_manager is manager1

    def test_get_config(self):
        from conversor.utils.config import config_manager
        config = config_manager.get_config()
        assert config is not None
        assert hasattr(config, "max_workers")

    def test_update_config(self):
        from conversor.utils.config import config_manager
        original = config_manager.get_config().max_workers
        config_manager.update_config(max_workers=4)
        assert config_manager.get_config().max_workers == 4
        config_manager.update_config(max_workers=original)

    def test_get_history(self):
        from conversor.utils.config import config_manager
        history = config_manager.get_history()
        assert isinstance(history, list)

    def test_add_to_history(self):
        from conversor.utils.config import config_manager, ConversionRecord
        record = ConversionRecord(
            id="test1",
            source_path="test.docx",
            output_path="test.pdf",
            source_format="docx",
            output_format="pdf",
            category="document",
            status="completed",
            timestamp="2026-07-18T12:00:00",
            duration=1.0,
            file_size_before=1000,
            file_size_after=500,
        )
        config_manager.add_to_history(record)
        history = config_manager.get_history()
        assert len(history) > 0

    def test_clear_history(self):
        from conversor.utils.config import config_manager
        config_manager.clear_history()
        history = config_manager.get_history()
        assert len(history) == 0

    def test_get_history_stats(self):
        from conversor.utils.config import config_manager
        stats = config_manager.get_history_stats()
        assert isinstance(stats, dict)
