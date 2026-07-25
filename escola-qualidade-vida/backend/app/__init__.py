import os
from datetime import timedelta
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from app.extensions import db, jwt, migrate

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
from app.routers.dashboard import dashboard_bp


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    frontend_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "frontend", "public"))

    upload_folder = os.path.join(base_dir, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.url_map.strict_slashes = False

    _configure_cors(app)
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


def _configure_cors(app):
    origins_raw = os.environ.get("CORS_ORIGINS", "")
    if origins_raw.strip() == "*":
        origins = "*"
    elif origins_raw.strip():
        origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
    else:
        origins = [
            "http://localhost:8080",
            "http://localhost:8088",
            "http://127.0.0.1:8080",
            "http://127.0.0.1:8088",
        ]

    CORS(app, resources={r"/*": {"origins": origins}})


def _configure_database(app):
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        db_user = os.environ.get("DB_USER", "root")
        db_password = os.environ.get("DB_PASSWORD", "password")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "5432")
        db_name = os.environ.get("DB_NAME", "escola_db")
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)


def _configure_jwt(app):
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave-em-desenvolvimento")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
    jwt.init_app(app)


def _register_jwt_error_handlers(app):
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "token_expired",
            "message": "Token expirado. Faca login novamente."
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({
            "error": "invalid_token",
            "message": "Token invalido."
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
            return jsonify({"erro": "Arquivo nao encontrado"}), 404
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


def _configure_email(app):
    app.config["SMTP_SERVER"] = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    app.config["SMTP_PORT"] = int(os.environ.get("SMTP_PORT", 587))
    app.config["EMAIL_FROM"] = os.environ.get("EMAIL_FROM", "")
    app.config["EMAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD", "")
    app.config["FRONTEND_URL"] = os.environ.get("FRONTEND_URL", "http://localhost:8080")


def _register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cadastro_bp)
    app.register_blueprint(curso_bp)
    app.register_blueprint(turma_bp)
    app.register_blueprint(ocorrencia_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(aluno_bp)
    app.register_blueprint(consulta_aluno_bp)
    app.register_blueprint(upload_bp, url_prefix="/files")
    app.register_blueprint(usuario_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(dashboard_bp)
