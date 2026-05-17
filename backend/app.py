import os
from flask import Flask
from flask_cors import CORS
from config import config
from models import db

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.resume import resume_bp
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'healthy'}, 200
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 5000)),
        debug=os.getenv('DEBUG', True)
    )