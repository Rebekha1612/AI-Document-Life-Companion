from flask import Flask
from flask_cors import CORS
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from routes.document_routes import document_bp
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)