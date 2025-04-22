from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Configurações do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', 'root')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '3306')}/{os.environ.get('DB_NAME', 'escola_db')}"
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_secreta_32_caracteres_no_minimo')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa as extensões
    db.init_app(app)
    jwt.init_app(app)

    # Registra os blueprints
    from app.routers.auth_routes import auth_bp
    from app.routers.student_routes import student_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/students')

    return app
