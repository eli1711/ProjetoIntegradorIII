# app/__init__.py
import os
import logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from app.extensions import db, jwt

# Blueprints
from app.routers.auth_routes import auth_bp
from app.routers.cadastro import cadastro_bp
from app.routers.curso_routes import curso_bp
from app.routers.turma_routes import turma_bp
from app.routers.ocorrencia_routes import ocorrencia_bp
from app.routers.test_routes import test_bp
from app.routers.aluno import aluno_bp
from app.routers.consulta_aluno import consulta_aluno_bp
from app.routers.uploads_routes import upload_bp
from app.routers.usuario_routes import usuario_bp


def create_app():
    """Cria e configura a aplicação Flask, incluindo banco, JWT, CORS e rotas."""
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # pasta única de uploads: app/uploads
    upload_folder = os.path.join(base_dir, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    print(f"📂 Pasta de uploads configurada em: {upload_folder}")

    # 1) cria a instância do Flask primeiro
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, "frontend", "public"),
        static_url_path=""
    )

    # 2) só depois mexa no url_map / CORS
    app.url_map.strict_slashes = False  # aceita /rota e /rota/
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Configurações principais
    _configure_database(app)
    _configure_email(app)
    _configure_jwt(app)
    _configure_uploads(app, upload_folder)

    # Registro dos blueprints
    _register_blueprints(app)

    # Página inicial (frontend)
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app


def _configure_database(app):
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "password")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "escola_db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)


def _configure_jwt(app):
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "uma_chave_secreta_32_caracteres_no_minimo")
    jwt.init_app(app)


def _configure_uploads(app, upload_folder: str):
    app.config["UPLOAD_FOLDER"] = upload_folder
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.route("/uploads/<path:filename>")
    def serve_uploaded_file(filename):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        app.logger.info(f"🖼️ Servindo arquivo: {file_path}")
        if not os.path.exists(file_path):
            app.logger.warning(f"❌ Arquivo não encontrado: {file_path}")
            return jsonify({"erro": "Arquivo não encontrado"}), 404
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


def _configure_email(app):
    app.config["SMTP_SERVER"] = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    app.config["SMTP_PORT"] = int(os.environ.get("SMTP_PORT", 587))
    app.config["EMAIL_FROM"] = os.environ.get("EMAIL_FROM", "guifavero10@gmail.com")
    app.config["EMAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD", "xhfs wgey gede jdce")
    app.config["FRONTEND_URL"] = os.environ.get("FRONTEND_URL", "http://localhost:8080")


def _register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cadastro_bp, url_prefix="/cadastro")
    app.register_blueprint(curso_bp, url_prefix="/cursos")
    app.register_blueprint(turma_bp, url_prefix="/turmas")
    app.register_blueprint(ocorrencia_bp)  # já tem url_prefix no próprio blueprint
    app.register_blueprint(test_bp, url_prefix="/api")
    app.register_blueprint(aluno_bp, url_prefix="/alunos")
    app.register_blueprint(consulta_aluno_bp, url_prefix="/alunos")
    app.register_blueprint(upload_bp, url_prefix="/files")
    app.register_blueprint(usuario_bp)
