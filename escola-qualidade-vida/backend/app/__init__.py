import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.extensions import db, jwt
import logging
# Blueprints das rotas
from app.routers.auth_routes import auth_bp
from app.routers.cadastro import cadastro_bp
from app.routers.curso_routes import curso_bp
from app.routers.turma_routes import turma_bp
from app.routers.ocorrencia_routes import ocorrencia_bp
from app.routers.test_routes import test_bp
from app.routers.aluno import aluno_bp
from app.routers.consulta_aluno import consulta_aluno_bp
from app.routers.uploads_routes import upload_bp  # Rota de upload
from app.routers.usuario_routes import usuario_bp
def create_app():
    """
    Função de criação da aplicação Flask. Realiza configurações iniciais e
    registra todos os blueprints necessários para as rotas da API.
    """
    # Caminho base da aplicação
    base_dir = os.path.abspath(os.path.dirname(__file__))  # Obtém o diretório atual onde o arquivo __init__.py está localizado
    
    # Caminho correto para o diretório de uploads (dentro do container, em /backend/app/uploads)
    upload_folder = os.path.join(base_dir, 'backend', 'app', 'uploads')  # Configuração correta

    # Criação da aplicação Flask
    app = Flask(__name__, static_folder=os.path.join(base_dir, 'frontend', 'public'), static_url_path='')

    # Configuração do banco de dados (MySQL)
    _configure_database(app)

    # Configuração de JWT para autenticação
    _configure_jwt(app)

    # Habilitar CORS para permitir chamadas da API de domínios diferentes
    CORS(app)

    # Configuração da pasta de uploads
    os.makedirs(upload_folder, exist_ok=True)  # Cria a pasta uploads, se ela não existir
    _configure_uploads(app, upload_folder)

    # Registrar Blueprints
    _register_blueprints(app)

    # Rota principal que serve o index.html do frontend
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app


def _configure_database(app):
    """
    Configurações do banco de dados (MySQL) usando SQLAlchemy.
    """
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', 'password')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'escola_db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


def _configure_jwt(app):
    """
    Configura o JWT para autenticação na aplicação.
    """
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_secreta_32_caracteres_no_minimo')
    jwt.init_app(app)


def _register_blueprints(app):
    """
    Registra todos os blueprints necessários para as rotas da API.
    """
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
    app.register_blueprint(curso_bp, url_prefix='/cursos')
    app.register_blueprint(turma_bp, url_prefix='/turmas')
    app.register_blueprint(ocorrencia_bp, url_prefix='/ocorrencias')
    app.register_blueprint(test_bp, url_prefix='/api')
    app.register_blueprint(aluno_bp, url_prefix='/alunos')
    app.register_blueprint(consulta_aluno_bp, url_prefix='/alunos')
    app.register_blueprint(upload_bp, url_prefix='/files')  # Upload de arquivos
    app.register_blueprint(usuario_bp)

def _configure_uploads(app, upload_folder):
    """
    Configura o diretório de uploads para armazenar arquivos.
    """
    app.config['UPLOAD_FOLDER'] = upload_folder  # Configura o diretório de uploads para ser usado no Flask

    @app.route('/uploads/<filename>')
    def serve_uploaded_file(filename):
        """
        Serve o arquivo de upload a partir do diretório de uploads.
        """
        app.logger.debug(f"Buscando arquivo em: {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
