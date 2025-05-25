import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.extensions import db, jwt

from app.routers.aluno import aluno_bp

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_path = os.path.join(base_dir, os.pardir, os.pardir, 'frontend', 'public')
    app = Flask(__name__, static_folder=static_path, static_url_path='')

    # Configurações do banco de dados (MySQL)
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', 'password')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'escola_db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_secreta_32_caracteres_no_minimo')

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Registrar blueprints
    from app.routers.auth_routes import auth_bp
    from app.routers.cadastro import cadastro_bp
    from app.routers.curso_routes import curso_bp
    from app.routers.turma_routes import turma_bp
    from app.routers.ocorrencia_routes import ocorrencia_bp
    from app.routers.test_routes import test_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
    app.register_blueprint(curso_bp, url_prefix='/cursos')
    app.register_blueprint(turma_bp, url_prefix='/turmas')
    app.register_blueprint(ocorrencia_bp, url_prefix='/ocorrencias')
    app.register_blueprint(test_bp, url_prefix='/api')
    app.register_blueprint(aluno_bp, url_prefix='/alunos')

    # Definir caminho absoluto da pasta uploads (ajuste o caminho se necessário)
    UPLOAD_FOLDER = '/app/app/uploads'


    @app.route('/uploads/<filename>')
    def uploads(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)


    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
