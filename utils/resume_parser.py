"""
Handles pulling raw text and basic contact info out of uploaded resume files.
Supports PDF and DOCX. Everything here works on an in-memory uploaded file
object (e.g. what Streamlit's file_uploader gives you), not just file paths.
"""

import io
import re

import pdfplumber
import docx


def extract_text_from_pdf(file_obj) -> str:
    """Extract all text from a PDF file-like object."""
    text_parts = []
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_obj) -> str:
    """Extract all text from a DOCX file-like object."""
    document = docx.Document(file_obj)
    return "\n".join(p.text for p in document.paragraphs if p.text)


def parse_resume(uploaded_file) -> str:
    """
    Dispatch to the right parser based on file extension.
    `uploaded_file` is expected to have a `.name` attribute and be readable
    as bytes (this matches Streamlit's UploadedFile interface).
    """
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()
    file_stream = io.BytesIO(file_bytes)

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_stream)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_stream)
    else:
        raise ValueError(
            f"Unsupported file type for '{uploaded_file.name}'. "
            "Please upload a .pdf or .docx file."
        )


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")


def extract_contact_info(text: str) -> dict:
    """Pull an email and phone number out of resume text, if present."""
    email_match = EMAIL_PATTERN.search(text)
    phone_match = PHONE_PATTERN.search(text)
    return {
        "email": email_match.group(0) if email_match else "Not found",
        "phone": phone_match.group(0) if phone_match else "Not found",
    }
