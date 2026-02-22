import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PyPDF2 import PdfReader
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_pdf_file(file_storage: FileStorage, max_size_bytes: int):
    if not file_storage or not file_storage.filename:
        return False, "File is required"

    if not allowed_file(file_storage.filename):
        return False, "Only PDF files are allowed"

    file_storage.stream.seek(0, os.SEEK_END)
    file_size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    if file_size > max_size_bytes:
        return False, f"File exceeds max size ({max_size_bytes} bytes)"

    return True, None


def save_resume_file(file_storage: FileStorage, upload_folder: str):
    Path(upload_folder).mkdir(parents=True, exist_ok=True)
    safe_name = secure_filename(file_storage.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_name = f"{timestamp}_{uuid4().hex}_{safe_name}"
    file_path = os.path.join(upload_folder, unique_name)
    file_storage.save(file_path)
    return unique_name, file_path


def extract_text_from_pdf(file_path: str):
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()
