from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'translation-system-secret-key'

    from app.views.auth_views import auth_bp
    from app.views.translation_views import translation_bp
    from app.views.admin_views import admin_bp
    from app.views.api_views import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(translation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app