"""Tests for UI components with mocked widgets."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import customtkinter as ctk


@pytest.fixture(scope="module")
def mock_root():
    """Create a mock Tk root (one per module to avoid TclError)."""
    root = ctk.CTk()
    root.withdraw()
    yield root
    root.destroy()


class TestThemes:
    """Test theme constants."""

    def test_colors_dict_not_empty(self):
        from conversor.ui.themes import COLORS
        assert len(COLORS) > 0

    def test_colors_are_hex(self):
        from conversor.ui.themes import COLORS
        for key, value in COLORS.items():
            assert value.startswith("#"), f"Color {key} is not hex: {value}"

    def test_fonts_dict_not_empty(self):
        from conversor.ui.themes import FONTS
        assert len(FONTS) > 0

    def test_fonts_have_correct_structure(self):
        from conversor.ui.themes import FONTS
        for key, font in FONTS.items():
            assert isinstance(font, tuple), f"Font {key} is not tuple"
            assert len(font) >= 2, f"Font {key} has less than 2 elements"
            assert isinstance(font[0], str), f"Font {key} family is not string"
            assert isinstance(font[1], int), f"Font {key} size is not int"

    def test_sizes_dict_not_empty(self):
        from conversor.ui.themes import SIZES
        assert len(SIZES) > 0

    def test_sizes_are_positive(self):
        from conversor.ui.themes import SIZES
        for key, value in SIZES.items():
            if isinstance(value, (int, float)):
                assert value > 0, f"Size {key} is not positive: {value}"


class TestFilePanel:
    """Test FilePanel logic with mocked widgets."""

    def test_file_panel_creation(self, mock_root):
        from conversor.ui.file_panel import FilePanel
        panel = FilePanel(mock_root)
        assert panel is not None

    def test_add_files_empty_list(self, mock_root):
        from conversor.ui.file_panel import FilePanel
        panel = FilePanel(mock_root)
        panel.add_files([])
        assert len(panel.get_files()) == 0

    def test_clear_files(self, mock_root):
        from conversor.ui.file_panel import FilePanel
        panel = FilePanel(mock_root)
        panel.clear_files()
        assert len(panel.get_files()) == 0


class TestOptionsPanel:
    """Test OptionsPanel logic with mocked widgets."""

    def test_options_panel_creation(self, mock_root):
        from conversor.ui.options_panel import OptionsPanel
        panel = OptionsPanel(mock_root)
        assert panel is not None

    def test_update_files_empty(self, mock_root):
        from conversor.ui.options_panel import OptionsPanel
        panel = OptionsPanel(mock_root)
        panel.update_files([])

    def test_set_converting_true(self, mock_root):
        from conversor.ui.options_panel import OptionsPanel
        panel = OptionsPanel(mock_root)
        panel.set_converting(True)

    def test_set_converting_false(self, mock_root):
        from conversor.ui.options_panel import OptionsPanel
        panel = OptionsPanel(mock_root)
        panel.set_converting(False)


class TestProgressPanel:
    """Test ProgressPanel logic with mocked widgets."""

    def test_progress_panel_creation(self, mock_root):
        from conversor.ui.progress_panel import ProgressPanel
        panel = ProgressPanel(mock_root)
        assert panel is not None

    def test_add_task(self, mock_root):
        from conversor.ui.progress_panel import ProgressPanel
        from conversor.converters.base import ConversionTask, ConversionOptions, FileCategory
        from pathlib import Path

        panel = ProgressPanel(mock_root)

        task = ConversionTask(
            id="test1",
            source_path=Path("test.txt"),
            output_format="pdf",
            category=FileCategory.DOCUMENT,
            options=ConversionOptions(output_format="pdf"),
        )
        panel.add_task(task)

    def test_update_global_empty(self, mock_root):
        from conversor.ui.progress_panel import ProgressPanel
        panel = ProgressPanel(mock_root)
        panel.update_global({"total": 0, "completed": 0, "failed": 0, "in_progress": 0}, 0.0)

    def test_update_global_with_tasks(self, mock_root):
        from conversor.ui.progress_panel import ProgressPanel
        panel = ProgressPanel(mock_root)
        panel.update_global({"total": 5, "completed": 3, "failed": 1, "in_progress": 1}, 30.0)

    def test_clear_all(self, mock_root):
        from conversor.ui.progress_panel import ProgressPanel
        panel = ProgressPanel(mock_root)
        panel.clear_all()


class TestSettingsWindow:
    """Test SettingsWindow logic with mocked widgets."""

    def test_settings_window_creation(self, mock_root):
        from conversor.ui.settings_window import SettingsWindow
        window = SettingsWindow(mock_root)
        assert window is not None
        window.destroy()


class TestLogViewer:
    """Test LogViewer logic with mocked widgets."""

    def test_log_viewer_creation(self, mock_root):
        from conversor.ui.log_viewer import LogViewerWindow
        window = LogViewerWindow(mock_root)
        assert window is not None
        window.destroy()


class TestHistoryWindow:
    """Test HistoryWindow logic with mocked widgets."""

    def test_history_window_creation(self, mock_root):
        from conversor.ui.history_window import HistoryWindow
        window = HistoryWindow(mock_root)
        assert window is not None
        window.destroy()
