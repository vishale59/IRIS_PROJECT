"""
Resume text extraction from PDF and DOCX.
"""
import os


def extract_text_from_resume(filepath: str) -> str:
    """Extract plain text from a PDF or DOCX resume."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        return _extract_pdf(filepath)
    elif ext in ('.docx', '.doc'):
        return _extract_docx(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def _extract_pdf(filepath: str) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text.strip()
    except ImportError:
        # Fallback: try pdfminer
        try:
            from pdfminer.high_level import extract_text
            return extract_text(filepath).strip()
        except ImportError:
            raise RuntimeError("Install PyMuPDF or pdfminer.six to parse PDFs.")


def _extract_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except ImportError:
        raise RuntimeError("Install python-docx to parse DOCX files.")
