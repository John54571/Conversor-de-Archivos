"""Integration tests for document conversions."""
import pytest
from pathlib import Path
from conversor.converters.documents import DocumentConverter
from conversor.converters.base import ConversionTask, ConversionOptions, FileCategory


def _make_task(source_path: Path, output_format: str, output_dir: Path) -> ConversionTask:
    """Helper to create a ConversionTask."""
    return ConversionTask(
        id=f"test_{source_path.stem}_{output_format}",
        source_path=source_path,
        output_format=output_format,
        category=FileCategory.DOCUMENT,
        options=ConversionOptions(output_format=output_format, output_dir=str(output_dir)),
    )


class TestDocxConversions:
    """Test DOCX to various formats."""

    def test_docx_to_pdf(self, sample_docx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0

    def test_docx_to_pdf_with_tables(self, sample_docx_tables, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx_tables, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 100

    def test_docx_to_pdf_with_images(self, sample_docx_images, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx_images, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 100

    def test_docx_to_txt(self, sample_docx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx, "txt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".txt"
        content = result.read_text(encoding="utf-8")
        assert "Sample Document" in content

    def test_docx_to_html(self, sample_docx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx, "html", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".html"
        content = result.read_text(encoding="utf-8")
        assert "<html>" in content

    def test_docx_to_odt(self, sample_docx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx, "odt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".odt"
        assert result.stat().st_size > 0

    def test_docx_to_epub(self, sample_docx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx, "epub", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".epub"
        assert result.stat().st_size > 0


class TestPdfConversions:
    """Test PDF to various formats."""

    def test_pdf_to_docx(self, sample_pdf, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_pdf, "docx", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".docx"
        assert result.stat().st_size > 0

    def test_pdf_to_txt(self, sample_pdf, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_pdf, "txt", temp_dir)
        # Disable OCR for this test (requires Poppler)
        from conversor.utils.config import config_manager
        original_ocr = config_manager.get_config().enable_ocr
        config_manager.update_config(enable_ocr=False)
        try:
            result = converter.convert(task)
            assert result.exists()
            assert result.suffix == ".txt"
            content = result.read_text(encoding="utf-8")
            assert "Sample PDF" in content
        finally:
            config_manager.update_config(enable_ocr=original_ocr)

    def test_pdf_to_html(self, sample_pdf, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_pdf, "html", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".html"
        content = result.read_text(encoding="utf-8")
        assert "<html>" in content


class TestXlsxConversions:
    """Test XLSX to various formats."""

    def test_xlsx_to_csv(self, sample_xlsx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_xlsx, "csv", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".csv"
        content = result.read_text(encoding="utf-8")
        assert "Alice" in content
        assert "Bob" in content

    def test_xlsx_to_txt(self, sample_xlsx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_xlsx, "txt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".txt"
        content = result.read_text(encoding="utf-8")
        assert "Alice" in content

    def test_xlsx_to_html(self, sample_xlsx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_xlsx, "html", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".html"
        content = result.read_text(encoding="utf-8")
        assert "<table>" in content or "Alice" in content

    def test_xlsx_to_pdf(self, sample_xlsx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_xlsx, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0


class TestCsvConversions:
    """Test CSV to various formats."""

    def test_csv_to_xlsx(self, sample_csv, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_csv, "xlsx", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".xlsx"
        assert result.stat().st_size > 0

    def test_csv_to_txt(self, sample_csv, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_csv, "txt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".txt"
        content = result.read_text(encoding="utf-8")
        assert "Alice" in content

    def test_csv_to_html(self, sample_csv, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_csv, "html", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".html"
        content = result.read_text(encoding="utf-8")
        assert "table" in content
        assert "Alice" in content

    def test_csv_to_pdf(self, sample_csv, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_csv, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0


class TestTxtConversions:
    """Test TXT to various formats."""

    def test_txt_to_pdf(self, sample_txt, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_txt, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0

    def test_txt_to_docx(self, sample_txt, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_txt, "docx", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".docx"
        assert result.stat().st_size > 0

    def test_txt_to_html(self, sample_txt, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_txt, "html", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".html"
        content = result.read_text(encoding="utf-8")
        assert "<html>" in content

    def test_txt_to_csv(self, sample_txt, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_txt, "csv", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".csv"
        assert result.stat().st_size > 0

    def test_txt_to_xlsx(self, sample_txt, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_txt, "xlsx", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".xlsx"
        assert result.stat().st_size > 0

    def test_txt_to_odt(self, sample_txt, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_txt, "odt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".odt"
        assert result.stat().st_size > 0

    def test_txt_to_epub(self, sample_txt, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_txt, "epub", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".epub"
        assert result.stat().st_size > 0


class TestHtmlConversions:
    """Test HTML to various formats."""

    def test_html_to_pdf(self, sample_html, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_html, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0

    def test_html_to_txt(self, sample_html, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_html, "txt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".txt"
        content = result.read_text(encoding="utf-8")
        assert "Sample HTML" in content

    def test_html_to_docx(self, sample_html, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_html, "docx", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".docx"
        assert result.stat().st_size > 0


class TestRtfConversions:
    """Test RTF to various formats."""

    def test_rtf_to_txt(self, sample_rtf, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_rtf, "txt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".txt"
        content = result.read_text(encoding="utf-8")
        assert "Sample RTF" in content

    def test_rtf_to_pdf(self, sample_rtf, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_rtf, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0

    def test_rtf_to_docx(self, sample_rtf, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_rtf, "docx", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".docx"
        assert result.stat().st_size > 0


class TestPptxConversions:
    """Test PPTX to various formats."""

    def test_pptx_to_pdf(self, sample_pptx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_pptx, "pdf", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".pdf"
        assert result.stat().st_size > 0

    def test_pptx_to_txt(self, sample_pptx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_pptx, "txt", temp_dir)
        result = converter.convert(task)
        assert result.exists()
        assert result.suffix == ".txt"
        content = result.read_text(encoding="utf-8")
        assert "Sample Presentation" in content


class TestOdtConversions:
    """Test ODT to various formats."""

    def test_odt_to_txt(self, sample_docx, temp_dir):
        converter = DocumentConverter()
        task = _make_task(sample_docx, "odt", temp_dir)
        odt_path = converter.convert(task)
        assert odt_path.exists()

        task2 = _make_task(odt_path, "txt", temp_dir)
        result = converter.convert(task2)
        assert result.exists()
        assert result.suffix == ".txt"
        content = result.read_text(encoding="utf-8")
        assert "Sample Document" in content
