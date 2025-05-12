from flask import Flask
from app.routers.cadastro import cadastro_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(cadastro_bp)
    return app
