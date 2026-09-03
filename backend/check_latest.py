from app import create_app
from models import Document

app = create_app()

with app.app_context():
    doc = Document.query.filter_by(filename='ritha.pdf').first()
    if doc:
        print(f"Filename: {doc.filename}")
        print(f"Extracted text:\n{repr(doc.extracted_text)}")
    else:
        print("Document not found")