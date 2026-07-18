import os
from pathlib import Path

from .base import BaseConverter, ConversionTask, ConversionOptions, FileCategory
from ..core.registry import ConverterRegistry
from ..utils.config import config_manager
from ..utils.logger import logger


@ConverterRegistry.register
class DocumentConverter(BaseConverter):
    SUPPORTED_INPUT = [
        "docx", "pdf", "xlsx", "csv", "pptx", "txt", "rtf", "html", "epub", "odt"
    ]
    SUPPORTED_OUTPUT = [
        "docx", "pdf", "xlsx", "csv", "txt", "html", "epub", "odt"
    ]
    CATEGORY = FileCategory.DOCUMENT

    BLOCKED_CONVERSIONS = {
        ("xlsx", "docx"), ("csv", "docx"),
        ("docx", "xlsx"), ("docx", "csv"),
        ("pdf", "xlsx"), ("pdf", "csv"),
        ("pptx", "xlsx"), ("pptx", "csv"),
    }

    @classmethod
    def can_convert(cls, source_ext: str, target_ext: str) -> bool:
        src = source_ext.lower().lstrip(".")
        tgt = target_ext.lower().lstrip(".")
        if (src, tgt) in cls.BLOCKED_CONVERSIONS:
            return False
        if src == tgt:
            return False
        return (src in cls.SUPPORTED_INPUT and tgt in cls.SUPPORTED_OUTPUT)

    @classmethod
    def get_valid_outputs(cls, source_ext: str) -> list[str]:
        ext = source_ext.lower().lstrip(".")
        if ext not in cls.SUPPORTED_INPUT:
            return []
        outputs = []
        for fmt in cls.SUPPORTED_OUTPUT:
            if fmt != ext and (ext, fmt) not in cls.BLOCKED_CONVERSIONS:
                outputs.append(fmt)
        return outputs

    def convert(self, task: ConversionTask) -> Path:
        src = task.source_path
        src_ext = src.suffix.lower().lstrip(".")
        tgt_ext = task.output_format.lower()
        output = task.options.output_dir or str(src.parent)
        output_path = Path(output) / f"{src.stem}.{tgt_ext}"

        Path(output).mkdir(parents=True, exist_ok=True)

        converters = {
            ("docx", "pdf"): self._docx_to_pdf,
            ("pdf", "docx"): self._pdf_to_docx,
            ("xlsx", "csv"): self._xlsx_to_csv,
            ("csv", "xlsx"): self._csv_to_xlsx,
            ("txt", "pdf"): self._txt_to_pdf,
            ("html", "pdf"): self._html_to_pdf,
            ("docx", "txt"): self._docx_to_txt,
            ("pdf", "txt"): self._pdf_to_txt,
            ("txt", "docx"): self._txt_to_docx,
            ("txt", "html"): self._txt_to_html,
            ("html", "txt"): self._html_to_txt,
            ("docx", "html"): self._docx_to_html,
            ("html", "docx"): self._html_to_docx,
            ("pptx", "pdf"): self._pptx_to_pdf,
            ("csv", "txt"): self._csv_to_txt,
            ("xlsx", "txt"): self._xlsx_to_txt,
            ("rtf", "txt"): self._rtf_to_txt,
            ("rtf", "pdf"): self._rtf_to_pdf,
            ("rtf", "docx"): self._rtf_to_docx,
            ("rtf", "html"): self._rtf_to_html,
            ("epub", "txt"): self._epub_to_txt,
            ("epub", "html"): self._epub_to_html,
            ("epub", "pdf"): self._epub_to_pdf,
            ("odt", "txt"): self._odt_to_txt,
            ("odt", "pdf"): self._odt_to_pdf,
            ("odt", "docx"): self._odt_to_docx,
        }

        handler = converters.get((src_ext, tgt_ext))
        if handler:
            handler(src, output_path, task)
        else:
            raise ValueError(f"Conversion no soportada: {src_ext} -> {tgt_ext}")

        return output_path

    def _docx_to_pdf(self, src: Path, dst: Path, task: ConversionTask):
        from docx import Document
        from fpdf import FPDF

        doc = Document(str(src))
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)

        for para in doc.paragraphs:
            text = para.text
            if text.strip():
                pdf.multi_cell(w=190, h=6, text=text)
            else:
                pdf.ln(4)

        if task.on_progress:
            task.on_progress(0.5)

        pdf.output(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _pdf_to_docx(self, src: Path, dst: Path, task: ConversionTask):
        from pdf2docx import Converter as Pdf2DocxConverter

        cv = Pdf2DocxConverter(str(src))
        cv.convert(str(dst))
        cv.close()

        if task.on_progress:
            task.on_progress(1.0)

    def _xlsx_to_csv(self, src: Path, dst: Path, task: ConversionTask):
        import pandas as pd

        df = pd.read_excel(str(src), sheet_name=0)
        df.to_csv(str(dst), index=False, encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _csv_to_xlsx(self, src: Path, dst: Path, task: ConversionTask):
        import pandas as pd

        df = pd.read_csv(str(src))
        df.to_excel(str(dst), index=False, engine="openpyxl")

        if task.on_progress:
            task.on_progress(1.0)

    def _txt_to_pdf(self, src: Path, dst: Path, task: ConversionTask):
        from fpdf import FPDF

        text = src.read_text(encoding="utf-8")
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Courier", size=10)

        for line in text.split("\n"):
            pdf.multi_cell(w=190, h=5, text=line)

        if task.on_progress:
            task.on_progress(0.7)

        pdf.output(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _html_to_pdf(self, src: Path, dst: Path, task: ConversionTask):
        from fpdf import FPDF
        import re

        html_content = src.read_text(encoding="utf-8")
        text = re.sub(r"<[^>]+>", "", html_content)
        text = re.sub(r"\s+", " ", text).strip()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(w=190, h=6, text=text)

        if task.on_progress:
            task.on_progress(0.7)

        pdf.output(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _docx_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        from docx import Document

        doc = Document(str(src))
        text = "\n".join(para.text for para in doc.paragraphs)
        dst.write_text(text, encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _pdf_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        use_ocr = config_manager.get_config().enable_ocr

        if use_ocr:
            self._pdf_to_txt_ocr(src, dst, task)
        else:
            self._pdf_to_txt_basic(src, dst, task)

    def _pdf_to_txt_basic(self, src: Path, dst: Path, task: ConversionTask):
        from pypdf import PdfReader

        reader = PdfReader(str(src))
        text_parts = []
        total = len(reader.pages)

        for i, page in enumerate(reader.pages):
            text_parts.append(page.extract_text() or "")
            if task.on_progress:
                task.on_progress((i + 1) / total * 0.9)

        dst.write_text("\n\n".join(text_parts), encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _pdf_to_txt_ocr(self, src: Path, dst: Path, task: ConversionTask):
        try:
            from pdf2image import convert_from_path
            from paddleocr import PaddleOCR

            ocr = PaddleOCR(use_angle_cls=True, lang=config_manager.get_config().ocr_language)
            
            images = convert_from_path(str(src))
            text_parts = []
            total = len(images)

            for i, img in enumerate(images):
                img_path = src.parent / f"_temp_page_{i}.png"
                img.save(str(img_path))
                
                result = ocr.ocr(str(img_path), cls=True)
                page_text = ""
                if result and result[0]:
                    for line in result[0]:
                        if line and len(line) > 1:
                            page_text += line[1][0] + "\n"
                
                text_parts.append(page_text)
                
                if img_path.exists():
                    img_path.unlink()
                
                if task.on_progress:
                    task.on_progress((i + 1) / total * 0.9)

            dst.write_text("\n\n".join(text_parts), encoding="utf-8")

            if task.on_progress:
                task.on_progress(1.0)

        except ImportError as e:
            logger.warning(f"PaddleOCR no disponible, usando extracción básica: {e}")
            self._pdf_to_txt_basic(src, dst, task)
        except Exception as e:
            logger.error(f"Error en OCR: {e}")
            raise ValueError(f"Error en OCR: {e}")

    def _txt_to_docx(self, src: Path, dst: Path, task: ConversionTask):
        from docx import Document

        text = src.read_text(encoding="utf-8")
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)
        doc.save(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _txt_to_html(self, src: Path, dst: Path, task: ConversionTask):
        text = src.read_text(encoding="utf-8")
        html = f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>{src.stem}</title></head>\n<body>\n"
        for line in text.split("\n"):
            html += f"<p>{line}</p>\n" if line.strip() else "<br>\n"
        html += "</body>\n</html>"
        dst.write_text(html, encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _html_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        import re

        html = src.read_text(encoding="utf-8")
        text = re.sub(r"<br\s*/?>", "\n", html)
        text = re.sub(r"</p>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        dst.write_text(text.strip(), encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _docx_to_html(self, src: Path, dst: Path, task: ConversionTask):
        from docx import Document

        doc = Document(str(src))
        html = f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>{src.stem}</title></head>\n<body>\n"
        for para in doc.paragraphs:
            if para.text.strip():
                html += f"<p>{para.text}</p>\n"
        html += "</body>\n</html>"
        dst.write_text(html, encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _html_to_docx(self, src: Path, dst: Path, task: ConversionTask):
        import re
        from docx import Document

        html = src.read_text(encoding="utf-8")
        text = re.sub(r"<br\s*/?>", "\n", html)
        text = re.sub(r"</p>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)

        doc = Document()
        for line in text.split("\n"):
            if line.strip():
                doc.add_paragraph(line.strip())
        doc.save(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _pptx_to_pdf(self, src: Path, dst: Path, task: ConversionTask):
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from fpdf import FPDF
        from PIL import Image
        import io

        prs = Presentation(str(src))
        pdf = FPDF()
        total = len(prs.slides)

        for i, slide in enumerate(prs.slides):
            pdf.add_page()
            
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, f"Slide {i + 1}", ln=True)
            pdf.ln(5)

            for shape in slide.shapes:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        if para.text.strip():
                            pdf.set_font("Helvetica", size=12)
                            pdf.multi_cell(w=190, h=6, text=para.text)
                            pdf.ln(2)
                
                if shape.shape_type == 13:
                    try:
                        image = shape.image
                        image_bytes = image.blob
                        img = Image.open(io.BytesIO(image_bytes))
                        
                        temp_img_path = src.parent / f"_temp_slide_img_{i}_{id(shape)}.png"
                        img.save(str(temp_img_path))
                        
                        pdf.image(str(temp_img_path), x=10, y=pdf.get_y(), w=100)
                        pdf.ln(img.height * 0.2 + 5)
                        
                        if temp_img_path.exists():
                            temp_img_path.unlink()
                    except Exception as e:
                        logger.debug(f"No se pudo insertar imagen en slide {i+1}: {e}")

            if task.on_progress:
                task.on_progress((i + 1) / total * 0.9)

        pdf.output(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _csv_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        text = src.read_text(encoding="utf-8")
        dst.write_text(text, encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _xlsx_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        import pandas as pd

        df = pd.read_excel(str(src), sheet_name=0)
        dst.write_text(df.to_string(index=False), encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _rtf_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        import re

        rtf = src.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"\\par\b", "\n", rtf)
        text = re.sub(r"\{[^}]*\}", "", text)
        text = re.sub(r"\\\w+\d*\s?", "", text)
        text = re.sub(r"[{}]", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        dst.write_text(text.strip(), encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _rtf_to_pdf(self, src: Path, dst: Path, task: ConversionTask):
        import re
        from fpdf import FPDF

        rtf = src.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"\\par\b", "\n", rtf)
        text = re.sub(r"\{[^}]*\}", "", text)
        text = re.sub(r"\\\w+\d*\s?", "", text)
        text = re.sub(r"[{}]", "", text)
        text = text.strip()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(w=190, h=6, text=text)

        if task.on_progress:
            task.on_progress(0.7)

        pdf.output(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _rtf_to_docx(self, src: Path, dst: Path, task: ConversionTask):
        import re
        from docx import Document

        rtf = src.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"\\par\b", "\n", rtf)
        text = re.sub(r"\{[^}]*\}", "", text)
        text = re.sub(r"\\\w+\d*\s?", "", text)
        text = re.sub(r"[{}]", "", text)
        text = text.strip()

        doc = Document()
        for line in text.split("\n"):
            if line.strip():
                doc.add_paragraph(line.strip())
        doc.save(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _rtf_to_html(self, src: Path, dst: Path, task: ConversionTask):
        import re

        rtf = src.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"\\par\b", "\n", rtf)
        text = re.sub(r"\{[^}]*\}", "", text)
        text = re.sub(r"\\\w+\d*\s?", "", text)
        text = re.sub(r"[{}]", "", text)
        text = text.strip()

        html = f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>{src.stem}</title></head>\n<body>\n"
        for line in text.split("\n"):
            html += f"<p>{line}</p>\n" if line.strip() else "<br>\n"
        html += "</body>\n</html>"
        dst.write_text(html, encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _epub_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        from ebooklib import epub
        from bs4 import BeautifulSoup

        book = epub.read_epub(str(src))
        text_parts = []
        items = list(book.get_items_of_type(9))
        total = len(items)

        for i, item in enumerate(items):
            html_content = item.get_content().decode("utf-8")
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text()
            text_parts.append(text)
            
            if task.on_progress:
                task.on_progress((i + 1) / total * 0.9)

        dst.write_text("\n\n".join(text_parts), encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _epub_to_html(self, src: Path, dst: Path, task: ConversionTask):
        from ebooklib import epub

        book = epub.read_epub(str(src))
        html_parts = []
        items = list(book.get_items_of_type(9))
        total = len(items)

        for i, item in enumerate(items):
            html_content = item.get_content().decode("utf-8")
            html_parts.append(html_content)
            
            if task.on_progress:
                task.on_progress((i + 1) / total * 0.9)

        combined = "\n\n".join(html_parts)
        dst.write_text(combined, encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _epub_to_pdf(self, src: Path, dst: Path, task: ConversionTask):
        from ebooklib import epub
        from bs4 import BeautifulSoup
        from fpdf import FPDF

        book = epub.read_epub(str(src))
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)

        items = list(book.get_items_of_type(9))
        total = len(items)

        for i, item in enumerate(items):
            html_content = item.get_content().decode("utf-8")
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text()
            
            for line in text.split("\n"):
                if line.strip():
                    pdf.multi_cell(w=190, h=6, text=line.strip())
            
            if task.on_progress:
                task.on_progress((i + 1) / total * 0.9)

        pdf.output(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _odt_to_txt(self, src: Path, dst: Path, task: ConversionTask):
        import zipfile
        from xml.etree import ElementTree as ET

        with zipfile.ZipFile(str(src), "r") as z:
            content_xml = z.read("content.xml")
        
        root = ET.fromstring(content_xml)
        text_parts = []
        
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())

        dst.write_text("\n".join(text_parts), encoding="utf-8")

        if task.on_progress:
            task.on_progress(1.0)

    def _odt_to_pdf(self, src: Path, dst: Path, task: ConversionTask):
        import zipfile
        from xml.etree import ElementTree as ET
        from fpdf import FPDF

        with zipfile.ZipFile(str(src), "r") as z:
            content_xml = z.read("content.xml")
        
        root = ET.fromstring(content_xml)
        text_parts = []
        
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)

        for text in text_parts:
            pdf.multi_cell(w=190, h=6, text=text)

        if task.on_progress:
            task.on_progress(0.7)

        pdf.output(str(dst))

        if task.on_progress:
            task.on_progress(1.0)

    def _odt_to_docx(self, src: Path, dst: Path, task: ConversionTask):
        import zipfile
        from xml.etree import ElementTree as ET
        from docx import Document

        with zipfile.ZipFile(str(src), "r") as z:
            content_xml = z.read("content.xml")
        
        root = ET.fromstring(content_xml)
        text_parts = []
        
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())

        doc = Document()
        for text in text_parts:
            doc.add_paragraph(text)
        doc.save(str(dst))

        if task.on_progress:
            task.on_progress(1.0)
