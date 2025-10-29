from flask import Flask
from .extensions import db, login_manager
from .routes import main_bp, auth_bp, bizready_bp, api_bp
from .models import *  # noqa

def create_app(config_object='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(bizready_bp)
    app.register_blueprint(api_bp)

    return app
