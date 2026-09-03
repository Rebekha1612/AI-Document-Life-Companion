from datetime import date
from flask import Blueprint, request, jsonify, current_app, send_file
import os
from werkzeug.utils import secure_filename

from models import db, Document, Reminder
from services.ocr_service import extract_text_from_file
from services.ai_service import classify_document, summarize_document, extract_key_details
from services.reminder_service import find_reminders

document_bp = Blueprint('documents', __name__)


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


@document_bp.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    extracted_text = extract_text_from_file(filepath)

    # Check for duplicates - same extracted text already exists
    if extracted_text and len(extracted_text.strip()) > 10:
        existing = Document.query.filter_by(extracted_text=extracted_text).first()
        if existing:
            os.remove(filepath)  # remove the newly saved duplicate file
            return jsonify({
                'error': f'This document appears to be a duplicate of "{existing.filename}" (uploaded {existing.uploaded_at.strftime("%Y-%m-%d")}).'
            }), 409

    category = classify_document(extracted_text)
    summary = summarize_document(extracted_text)
    key_details = extract_key_details(extracted_text)
    reminder_data = find_reminders(extracted_text)

    new_doc = Document(
        filename=filename,
        filepath=filepath,
        extracted_text=extracted_text,
        category=category,
        summary=summary,
        key_details=key_details
    )
    db.session.add(new_doc)
    db.session.commit()

    for r in reminder_data:
        reminder = Reminder(
            document_id=new_doc.id,
            label=r['label'],
            due_date=r['due_date']
        )
        db.session.add(reminder)

    db.session.commit()

    return jsonify(new_doc.to_dict()), 201


@document_bp.route('/', methods=['GET'])
def get_all_documents():
    category = request.args.get('category')

    query = Document.query
    if category:
        query = query.filter_by(category=category)

    documents = query.order_by(Document.uploaded_at.desc()).all()
    return jsonify([doc.to_dict() for doc in documents]), 200


@document_bp.route('/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return jsonify(doc.to_dict()), 200


@document_bp.route('/<int:doc_id>/file', methods=['GET'])
def get_document_file(doc_id):
    """Serves the actual uploaded file (image/PDF) so it can be viewed/downloaded."""
    doc = Document.query.get_or_404(doc_id)

    if not os.path.exists(doc.filepath):
        return jsonify({'error': 'File not found on server'}), 404

    return send_file(doc.filepath)


@document_bp.route('/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    if os.path.exists(doc.filepath):
        os.remove(doc.filepath)

    db.session.delete(doc)
    db.session.commit()

    return jsonify({'message': 'Document deleted'}), 200


@document_bp.route('/reminders/upcoming', methods=['GET'])
def get_upcoming_reminders():
    reminders = Reminder.query.order_by(Reminder.due_date.asc()).all()
    result = []
    for r in reminders:
        data = r.to_dict()
        data['document_name'] = r.document.filename
        result.append(data)
    return jsonify(result), 200


@document_bp.route('/health-summary', methods=['GET'])
def get_health_summary():
    all_reminders = Reminder.query.all()
    today = date.today()

    expired = 0
    expiring_soon = 0

    doc_ids_with_reminders = set()

    for r in all_reminders:
        doc_ids_with_reminders.add(r.document_id)
        days_left = (r.due_date - today).days
        if days_left < 0:
            expired += 1
        elif days_left <= 30:
            expiring_soon += 1

    total_docs = Document.query.count()
    valid = total_docs - len(doc_ids_with_reminders) + (len(doc_ids_with_reminders) - expired - expiring_soon)

    return jsonify({
        'total_documents': total_docs,
        'expired': expired,
        'expiring_soon': expiring_soon,
        'valid': max(valid, 0)
    }), 200
