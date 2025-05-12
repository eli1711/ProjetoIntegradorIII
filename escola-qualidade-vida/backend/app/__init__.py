import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Instanciações globais (extensões)
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    # Configuração da aplicação Flask
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_path = os.path.join(base_dir, os.pardir, os.pardir, 'frontend', 'public')
    app = Flask(__name__, static_folder=static_path, static_url_path='')

    # Configurações de banco de dados (MySQL por padrão, via variáveis de ambiente)
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', 'password')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'escola_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_secreta_32_caracteres_no_minimo')

    # Inicializa extensões no app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)  # libera CORS para todas as rotas

    # Registro de blueprints (rotas)
    from app.routers.auth_routes import auth_bp
    from app.routers.cadastro import cadastro_bp
    from app.routers.curso_routes import curso_bp
    from app.routers.turma_routes import turma_bp
    from app.routers.ocorrencia_routes import ocorrencia_bp
    from app.routers.test_routes import test_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cadastro_bp)        # /alunos (prefixo definido no blueprint)
    app.register_blueprint(curso_bp)           # /cursos
    app.register_blueprint(turma_bp)           # /turmas
    app.register_blueprint(ocorrencia_bp)      # /ocorrencias
    app.register_blueprint(test_bp, url_prefix='/api')

    # Rota padrão para servir a página inicial (frontend)
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
