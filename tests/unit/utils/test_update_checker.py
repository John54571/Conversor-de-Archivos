"""Tests for update checker."""
import pytest
from unittest.mock import patch, MagicMock
import json


class TestParseVersion:
    """Test parse_version function."""

    def test_simple_version(self):
        from conversor.utils.update_checker import parse_version
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_version_with_v_prefix(self):
        from conversor.utils.update_checker import parse_version
        assert parse_version("v1.2.3") == (1, 2, 3)

    def test_version_with_text(self):
        from conversor.utils.update_checker import parse_version
        assert parse_version("release-v1.5.0") == (1, 5, 0)

    def test_invalid_version(self):
        from conversor.utils.update_checker import parse_version
        assert parse_version("invalid") == (0, 0, 0)

    def test_empty_string(self):
        from conversor.utils.update_checker import parse_version
        assert parse_version("") == (0, 0, 0)

    def test_partial_version(self):
        from conversor.utils.update_checker import parse_version
        # parse_version requires 3 parts, "1.2" doesn't match the regex
        assert parse_version("1.2") == (0, 0, 0)


class TestGetCurrentVersion:
    """Test get_current_version function."""

    def test_get_version_from_init(self):
        from conversor.utils.update_checker import get_current_version
        version = get_current_version()
        assert version != "0.0.0"
        assert "." in version

    @patch("sys.frozen", True, create=True)
    def test_get_version_frozen(self):
        from conversor.utils.update_checker import get_current_version
        version = get_current_version()
        assert version != "0.0.0"


class TestCheckForUpdates:
    """Test check_for_updates function."""

    @patch("urllib.request.urlopen")
    def test_no_update_available(self, mock_urlopen):
        from conversor.utils.update_checker import check_for_updates, get_current_version

        current = get_current_version()
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "tag_name": f"v{current}",
            "body": "No changes",
            "html_url": "https://github.com/test",
            "assets": [],
            "published_at": "2026-01-01",
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = check_for_updates()
        assert result is None

    @patch("urllib.request.urlopen")
    def test_update_available(self, mock_urlopen):
        from conversor.utils.update_checker import check_for_updates

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "tag_name": "v99.99.99",
            "body": "New version",
            "html_url": "https://github.com/test",
            "assets": [
                {
                    "name": "ConversorDeArchivos-Setup.exe",
                    "browser_download_url": "https://github.com/test/download/setup.exe",
                    "size": 1000000,
                }
            ],
            "published_at": "2026-01-01",
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = check_for_updates()
        assert result is not None
        assert result.version == "99.99.99"
        assert result.installer_url == "https://github.com/test/download/setup.exe"

    @patch("urllib.request.urlopen")
    def test_network_error(self, mock_urlopen):
        from conversor.utils.update_checker import check_for_updates
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Network error")
        result = check_for_updates()
        assert result is None


class TestFormatFileSize:
    """Test format_file_size function."""

    def test_bytes(self):
        from conversor.utils.update_checker import format_file_size
        assert format_file_size(500) == "500 B"

    def test_kilobytes(self):
        from conversor.utils.update_checker import format_file_size
        assert "KB" in format_file_size(1500)

    def test_megabytes(self):
        from conversor.utils.update_checker import format_file_size
        assert "MB" in format_file_size(1500000)

    def test_zero(self):
        from conversor.utils.update_checker import format_file_size
        assert format_file_size(0) == "0 B"
