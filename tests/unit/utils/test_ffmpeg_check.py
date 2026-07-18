"""Tests for FFmpeg check utilities."""
import pytest
from unittest.mock import patch, MagicMock


class TestCheckFfmpeg:
    """Test check_ffmpeg function."""

    @patch("shutil.which")
    def test_ffmpeg_available(self, mock_which):
        from conversor.utils.ffmpeg_check import check_ffmpeg
        mock_which.return_value = "/usr/bin/ffmpeg"
        found, path = check_ffmpeg()
        assert found is True
        assert path != ""

    @patch("shutil.which")
    def test_ffmpeg_not_available(self, mock_which):
        from conversor.utils.ffmpeg_check import check_ffmpeg
        mock_which.return_value = None
        # Mock common paths to not exist
        with patch("pathlib.Path.is_dir", return_value=False):
            found, path = check_ffmpeg()
            assert found is False
            assert path == ""

    @patch("shutil.which")
    def test_ffmpeg_with_configured_path(self, mock_which):
        from conversor.utils.ffmpeg_check import check_ffmpeg
        mock_which.return_value = None
        # Simular ruta configurada válida
        with patch("pathlib.Path.is_file", return_value=True), \
             patch("pathlib.Path.name", "ffmpeg.exe"):
            found, path = check_ffmpeg("/usr/bin/ffmpeg.exe")
            assert found is True


class TestCheckFfmpegVersion:
    """Test check_ffmpeg_version function."""

    @patch("subprocess.run")
    def test_version_retrieved(self, mock_run):
        from conversor.utils.ffmpeg_check import check_ffmpeg_version
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="ffmpeg version 4.4.1\nCopyright...",
        )
        version = check_ffmpeg_version()
        assert version is not None
        assert "ffmpeg version" in version

    @patch("subprocess.run")
    def test_version_not_available(self, mock_run):
        from conversor.utils.ffmpeg_check import check_ffmpeg_version
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        version = check_ffmpeg_version()
        assert version is None

    @patch("subprocess.run")
    def test_timeout(self, mock_run):
        from conversor.utils.ffmpeg_check import check_ffmpeg_version
        mock_run.side_effect = Exception("Timeout")
        version = check_ffmpeg_version()
        assert version is None


class TestGetFfmpegPath:
    """Test get_ffmpeg_path function."""

    @patch("shutil.which")
    def test_path_found(self, mock_which):
        from conversor.utils.ffmpeg_check import get_ffmpeg_path
        mock_which.return_value = "/usr/bin/ffmpeg"
        path = get_ffmpeg_path()
        assert path is not None

    @patch("shutil.which")
    def test_path_not_found(self, mock_which):
        from conversor.utils.ffmpeg_check import get_ffmpeg_path
        mock_which.return_value = None
        with patch("pathlib.Path.is_dir", return_value=False):
            path = get_ffmpeg_path()
            assert path is None


class TestCheckFfprobe:
    """Test check_ffprobe function."""

    @patch("shutil.which")
    def test_ffprobe_available(self, mock_which):
        from conversor.utils.ffmpeg_check import check_ffprobe
        mock_which.return_value = "/usr/bin/ffprobe"
        assert check_ffprobe() is True

    @patch("shutil.which")
    def test_ffprobe_not_available(self, mock_which):
        from conversor.utils.ffmpeg_check import check_ffprobe
        mock_which.return_value = None
        with patch("pathlib.Path.is_dir", return_value=False):
            assert check_ffprobe() is False
