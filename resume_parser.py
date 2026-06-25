"""
resume_parser.py — Extracts text from PDF and DOCX resume files.
"""

import io
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from a PDF file uploaded via Streamlit."""
    try:
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        return f"[Error extracting PDF text: {e}]"


def extract_text_from_docx(uploaded_file) -> str:
    """Extract all text from a DOCX file uploaded via Streamlit."""
    try:
        doc = Document(io.BytesIO(uploaded_file.read()))
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(text_parts).strip()
    except Exception as e:
        return f"[Error extracting DOCX text: {e}]"


def extract_resume_text(uploaded_file) -> str:
    """
    Detect file type and extract text accordingly.
    Supports .pdf and .docx files.
    """
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return "[Unsupported file format. Please upload a PDF or DOCX file.]"
