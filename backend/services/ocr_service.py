import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

# Tell pytesseract exactly where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Tell pdf2image exactly where Poppler is installed
POPPLER_PATH = r'C:\Users\REBEKHA\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin'

def extract_text_from_file(filepath):
    ext = filepath.rsplit('.', 1)[-1].lower()

    try:
        if ext == 'pdf':
            return _extract_from_pdf(filepath)
        elif ext in ['png', 'jpg', 'jpeg']:
            return _extract_from_image(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""


def _extract_from_image(filepath):
    image = Image.open(filepath)
    text = pytesseract.image_to_string(image)
    return text.strip()


def _extract_from_pdf(filepath):
    pages = convert_from_path(filepath, poppler_path=POPPLER_PATH)
    full_text = ""

    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page)
        full_text += f"\n--- Page {i+1} ---\n{text}"

    return full_text.strip()