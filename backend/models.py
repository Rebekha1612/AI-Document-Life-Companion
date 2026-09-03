from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {'id': self.id, 'full_name': self.full_name, 'email': self.email, 'username': self.username}


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    key_details = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    reminders = db.relationship('Reminder', backref='document', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'category': self.category,
            'summary': self.summary,
            'key_details': self.key_details,
            'uploaded_at': self.uploaded_at.isoformat(),
            'reminders': [r.to_dict() for r in self.reminders]
        }


class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    is_notified = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'label': self.label,
            'due_date': self.due_date.isoformat(),
            'is_notified': self.is_notified
        }