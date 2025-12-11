import os
from datetime import timedelta
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
from app.routers.permission_routes import permission_bp
from app.routers.debug_routes import debug_bp
from .routers.dashboard import dashboard_bp 


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    upload_folder = os.path.join(base_dir, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, "frontend", "public"),
        static_url_path=""
    )

    app.url_map.strict_slashes = False
    CORS(app, resources={r"/*": {"origins": "*"}})

    _configure_database(app)
    _configure_email(app)
    _configure_jwt(app)
    _configure_uploads(app, upload_folder)

    _register_blueprints(app)
    _register_jwt_error_handlers(app)

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

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)


def _configure_jwt(app):
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "uma_chave_secreta_32_caracteres_no_minimo"
    )

    # ✅ define expiração explicitamente (não dependa do default)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

    jwt.init_app(app)


def _register_jwt_error_handlers(app):
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "token_expired",
            "message": "Token expirado. Faça login novamente."
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({
            "error": "invalid_token",
            "message": "Token inválido."
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({
            "error": "missing_token",
            "message": "Token ausente."
        }), 401


def _configure_uploads(app, upload_folder: str):
    app.config["UPLOAD_FOLDER"] = upload_folder
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.route("/uploads/<path:filename>")
    def serve_uploaded_file(filename):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(file_path):
            return jsonify({"erro": "Arquivo não encontrado"}), 404
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


def _configure_email(app):
    app.config["SMTP_SERVER"] = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    app.config["SMTP_PORT"] = int(os.environ.get("SMTP_PORT", 587))
    app.config["EMAIL_FROM"] = os.environ.get("EMAIL_FROM", "guifavero10@gmail.com")
    app.config["EMAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD", "sua_senha_app")
    app.config["FRONTEND_URL"] = os.environ.get("FRONTEND_URL", "http://localhost:8080")


def _register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cadastro_bp, url_prefix="/cadastro")
    app.register_blueprint(curso_bp, url_prefix="/cursos")
    app.register_blueprint(turma_bp, url_prefix="/turmas")
    app.register_blueprint(ocorrencia_bp)
    app.register_blueprint(test_bp, url_prefix="/api")
    app.register_blueprint(aluno_bp)
    app.register_blueprint(consulta_aluno_bp, url_prefix="/alunos")
    app.register_blueprint(upload_bp, url_prefix="/files")
    app.register_blueprint(usuario_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(dashboard_bp)
