"""Shared fixtures for all tests."""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def sample_files_dir():
    """Return path to sample files directory."""
    return Path(__file__).parent / "fixtures" / "sample_files"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    dirpath = tempfile.mkdtemp()
    yield Path(dirpath)
    shutil.rmtree(dirpath, ignore_errors=True)


@pytest.fixture
def sample_docx(sample_files_dir):
    """Return path to sample DOCX file."""
    return sample_files_dir / "documents" / "sample.docx"


@pytest.fixture
def sample_docx_tables(sample_files_dir):
    """Return path to sample DOCX file with tables."""
    return sample_files_dir / "documents" / "sample_tables.docx"


@pytest.fixture
def sample_docx_images(sample_files_dir):
    """Return path to sample DOCX file with images."""
    return sample_files_dir / "documents" / "sample_images.docx"


@pytest.fixture
def sample_pdf(sample_files_dir):
    """Return path to sample PDF file."""
    return sample_files_dir / "documents" / "sample.pdf"


@pytest.fixture
def sample_xlsx(sample_files_dir):
    """Return path to sample XLSX file."""
    return sample_files_dir / "documents" / "sample.xlsx"


@pytest.fixture
def sample_csv(sample_files_dir):
    """Return path to sample CSV file."""
    return sample_files_dir / "documents" / "sample.csv"


@pytest.fixture
def sample_txt(sample_files_dir):
    """Return path to sample TXT file."""
    return sample_files_dir / "documents" / "sample.txt"


@pytest.fixture
def sample_html(sample_files_dir):
    """Return path to sample HTML file."""
    return sample_files_dir / "documents" / "sample.html"


@pytest.fixture
def sample_rtf(sample_files_dir):
    """Return path to sample RTF file."""
    return sample_files_dir / "documents" / "sample.rtf"


@pytest.fixture
def sample_pptx(sample_files_dir):
    """Return path to sample PPTX file."""
    return sample_files_dir / "documents" / "sample.pptx"


@pytest.fixture
def sample_png(sample_files_dir):
    """Return path to sample PNG file."""
    return sample_files_dir / "images" / "sample.png"


@pytest.fixture
def sample_png_rgba(sample_files_dir):
    """Return path to sample RGBA PNG file."""
    return sample_files_dir / "images" / "sample_rgba.png"


@pytest.fixture
def sample_jpg(sample_files_dir):
    """Return path to sample JPG file."""
    return sample_files_dir / "images" / "sample.jpg"


@pytest.fixture
def sample_jpg_large(sample_files_dir):
    """Return path to large sample JPG file."""
    return sample_files_dir / "images" / "sample_large.jpg"


@pytest.fixture
def sample_wav(sample_files_dir):
    """Return path to sample WAV file."""
    return sample_files_dir / "audio" / "sample.wav"
