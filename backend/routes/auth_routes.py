from flask import Blueprint, request, jsonify
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not full_name or not email or not username or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(full_name=full_name, email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify(user.to_dict()), 200


@auth_bp.route('/update-profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    user_id = data.get('user_id')
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()

    if not user_id or not full_name or not email:
        return jsonify({'error': 'All fields are required'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    existing_email = User.query.filter(User.email == email, User.id != user_id).first()
    if existing_email:
        return jsonify({'error': 'Email already in use by another account'}), 400

    user.full_name = full_name
    user.email = email
    db.session.commit()

    return jsonify(user.to_dict()), 200