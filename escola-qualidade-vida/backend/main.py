# main.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.routes.auth_routes import auth_bp
from app.routes.aluno_routes import aluno_bp
from app.routes.ocorrencia_routes import ocorrencia_bp

# Configurações
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "minha_chave_secreta")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+mysqlconnector://app_user:SenhaSegura123!@localhost:3306/projetoteste")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Inicializa o banco de dados
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
JWTManager(app)

# Registro dos Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(aluno_bp, url_prefix="/alunos")
app.register_blueprint(ocorrencia_bp, url_prefix="/ocorrencias")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)