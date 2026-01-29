
import os
import pypdf
from docx import Document

def extract_text_from_file(file_path):
    """
    Extracts text from a given file path.
    Supports .pdf, .docx, and .txt
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            return _extract_from_pdf(file_path)
        elif ext == '.docx':
            return _extract_from_docx(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"Error: Unsupported file type {ext}"
    except Exception as e:
        return f"Error parsing file: {str(e)}"

def _extract_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def _extract_from_docx(file_path):
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)

if __name__ == "__main__":
    # Test
    print("File parser module loaded.")
