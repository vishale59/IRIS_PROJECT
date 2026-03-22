"""Resume parsing and lightweight keyword analysis helpers."""

import os
import re
from typing import Iterable

DEFAULT_SKILLS = {
    "python",
    "flask",
    "django",
    "sql",
    "mysql",
    "html",
    "css",
    "javascript",
    "react",
    "git",
    "docker",
    "aws",
    "api",
    "testing",
    "linux",
}


def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF, DOCX, or plain-text DOC uploads."""
    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".pdf":
        return _extract_pdf(file_path)
    if extension == ".docx":
        return _extract_docx(file_path)
    if extension == ".doc":
        return _extract_doc(file_path)
    raise ValueError("Unsupported file type.")


def analyze_resume_keywords(resume_text: str, job_text: str = "") -> dict:
    """Score a resume by matching known skills against resume and job text."""
    resume_terms = set(_tokenize(resume_text))
    job_terms = set(_tokenize(job_text))
    reference_terms = job_terms or DEFAULT_SKILLS
    matched = sorted(skill for skill in reference_terms if skill in resume_terms)
    denominator = len(reference_terms) or 1
    score = int((len(matched) / denominator) * 100)
    return {
        "score": score,
        "keywords": matched[:20],
    }


def _extract_pdf(file_path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    return "\n".join((page.extract_text() or "") for page in reader).strip()


def _extract_docx(file_path: str) -> str:
    from docx import Document

    document = Document(file_path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()


def _extract_doc(file_path: str) -> str:
    with open(file_path, "rb") as uploaded_file:
        return uploaded_file.read().decode("latin-1", errors="ignore").strip()


def _tokenize(text: str) -> Iterable[str]:
    return re.findall(r"[a-zA-Z0-9\+\#\.]{2,}", text.lower())
