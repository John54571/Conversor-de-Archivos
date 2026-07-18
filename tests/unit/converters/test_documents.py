"""Tests for document converter - unit tests."""
import pytest
from conversor.converters.documents import DocumentConverter


class TestSanitizeText:
    """Test _sanitize_text method for Unicode character handling."""

    def test_smart_quotes_replacement(self):
        text = "\u201chello\u201d"
        result = DocumentConverter._sanitize_text(text)
        assert result == '"hello"'

    def test_single_smart_quotes(self):
        text = "\u2018hello\u2019"
        result = DocumentConverter._sanitize_text(text)
        assert result == "'hello'"

    def test_em_dash_replacement(self):
        text = "hello\u2014world"
        result = DocumentConverter._sanitize_text(text)
        assert result == "hello--world"

    def test_en_dash_replacement(self):
        text = "hello\u2013world"
        result = DocumentConverter._sanitize_text(text)
        assert result == "hello-world"

    def test_ellipsis_replacement(self):
        text = "hello\u2026"
        result = DocumentConverter._sanitize_text(text)
        assert result == "hello..."

    def test_non_breaking_space(self):
        text = "hello\u00a0world"
        result = DocumentConverter._sanitize_text(text)
        assert result == "hello world"

    def test_guillemets(self):
        text = "\u00abhello\u00bb"
        result = DocumentConverter._sanitize_text(text)
        assert result == '"hello"'

    def test_mixed_unicode(self):
        text = "\u201chello\u201d \u2014 world\u2026"
        result = DocumentConverter._sanitize_text(text)
        assert result == '"hello" -- world...'

    def test_plain_text_unchanged(self):
        text = "hello world"
        result = DocumentConverter._sanitize_text(text)
        assert result == "hello world"

    def test_empty_string(self):
        text = ""
        result = DocumentConverter._sanitize_text(text)
        assert result == ""


class TestCanConvert:
    """Test can_convert class method."""

    def test_docx_to_pdf(self):
        assert DocumentConverter.can_convert("docx", "pdf") is True

    def test_pdf_to_docx(self):
        assert DocumentConverter.can_convert("pdf", "docx") is True

    def test_xlsx_to_csv(self):
        assert DocumentConverter.can_convert("xlsx", "csv") is True

    def test_csv_to_xlsx(self):
        assert DocumentConverter.can_convert("csv", "xlsx") is True

    def test_txt_to_pdf(self):
        assert DocumentConverter.can_convert("txt", "pdf") is True

    def test_blocked_xlsx_to_docx(self):
        assert DocumentConverter.can_convert("xlsx", "docx") is False

    def test_blocked_csv_to_docx(self):
        assert DocumentConverter.can_convert("csv", "docx") is False

    def test_blocked_docx_to_xlsx(self):
        assert DocumentConverter.can_convert("docx", "xlsx") is False

    def test_blocked_docx_to_csv(self):
        assert DocumentConverter.can_convert("docx", "csv") is False

    def test_blocked_pdf_to_xlsx(self):
        assert DocumentConverter.can_convert("pdf", "xlsx") is False

    def test_blocked_pdf_to_csv(self):
        assert DocumentConverter.can_convert("pdf", "csv") is False

    def test_same_format(self):
        assert DocumentConverter.can_convert("docx", "docx") is False

    def test_unsupported_format(self):
        assert DocumentConverter.can_convert("xyz", "pdf") is False

    def test_case_insensitive(self):
        assert DocumentConverter.can_convert("DOCX", "PDF") is True

    def test_with_dot_prefix(self):
        assert DocumentConverter.can_convert(".docx", ".pdf") is True


class TestGetValidOutputs:
    """Test get_valid_outputs class method."""

    def test_docx_outputs(self):
        outputs = DocumentConverter.get_valid_outputs("docx")
        assert "pdf" in outputs
        assert "txt" in outputs
        assert "html" in outputs
        assert "odt" in outputs
        assert "epub" in outputs
        assert "xlsx" not in outputs
        assert "csv" not in outputs

    def test_pdf_outputs(self):
        outputs = DocumentConverter.get_valid_outputs("pdf")
        assert "docx" in outputs
        assert "txt" in outputs
        assert "html" in outputs
        assert "xlsx" not in outputs
        assert "csv" not in outputs

    def test_xlsx_outputs(self):
        outputs = DocumentConverter.get_valid_outputs("xlsx")
        assert "csv" in outputs
        assert "txt" in outputs
        assert "html" in outputs
        assert "pdf" in outputs
        assert "docx" not in outputs

    def test_csv_outputs(self):
        outputs = DocumentConverter.get_valid_outputs("csv")
        assert "xlsx" in outputs
        assert "txt" in outputs
        assert "html" in outputs
        assert "pdf" in outputs
        assert "docx" not in outputs

    def test_txt_outputs(self):
        outputs = DocumentConverter.get_valid_outputs("txt")
        assert "pdf" in outputs
        assert "docx" in outputs
        assert "html" in outputs
        assert "csv" in outputs
        assert "xlsx" in outputs

    def test_unsupported_format(self):
        outputs = DocumentConverter.get_valid_outputs("xyz")
        assert outputs == []
