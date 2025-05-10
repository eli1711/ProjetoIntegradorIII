import os
import time
import re
from flask import Flask, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash  # Embora não usemos mais hash, mantivemos para referência futura
from flask_cors import CORS  # Importando CORS para permitir requisições de outras origens
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
import jwt
from datetime import datetime, timedelta

# Inicializando a aplicação Flask
app = Flask(__name__, static_folder='frontend/public', static_url_path='')

# Ativando CORS para permitir todas as origens na API
CORS(app, resources={r"/auth/*": {"origins": "*"}})  # Permite todas as origens para rotas /auth

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', 'password')}@"
    f"{os.environ.get('DB_HOST', 'mysql')}:{os.environ.get('DB_PORT', '3306')}/{os.environ.get('DB_NAME', 'escola_db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_super_secreta_32_caracteres_no_minimo')  # Defina a chave secreta para JWT

# Inicializando o SQLAlchemy
db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)  # Senha em texto simples

# Blueprint de autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Função para esperar o banco de dados estar disponível (com backoff exponencial)
def wait_for_db():
    """Esperar até que o banco de dados esteja acessível."""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(db_uri)
    attempt = 0

    # Tenta conectar ao banco de dados até que a conexão seja bem-sucedida
    while True:
        try:
            with engine.connect() as connection:
                print("Conexão bem-sucedida com o banco de dados!")
                break
        except OperationalError:
            attempt += 1
            backoff_time = 2 ** attempt  # Backoff exponencial
            print(f"Banco de dados não disponível, tentando novamente em {backoff_time} segundos...")
            time.sleep(backoff_time)

@app.route('/')
def home():
    return "Bem-vindo à página inicial!"

def validate_email(email):
    """Função para validar o formato do e-mail."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@auth_bp.route('/login', methods=['POST'])
def login():
    """Rota de login que valida o e-mail e a senha do usuário."""
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    # Verifica se o e-mail e a senha foram fornecidos
    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    # Validação do formato do e-mail
    if not validate_email(email):
        return jsonify({"erro": "E-mail inválido"}), 400

    print(f"Recebendo login para o e-mail: {email}")  # Log para depuração

    # Verifica se o usuário existe no banco de dados
    usuario = Usuario.query.filter_by(email=email).first()

    # Se o usuário não for encontrado
    if not usuario:
        print(f"Usuário não encontrado para o e-mail: {email}")  # Log para depuração
        return jsonify({"erro": "E-mail ou senha inválidos"}), 401

    # Verifica se a senha fornecida é a mesma que a do banco de dados (sem hash)
    if usuario.senha != senha:
        print(f"Senha incorreta para o usuário: {email}")  # Log para depuração
        return jsonify({"erro": "E-mail ou senha inválidos"}), 401

    # Gerar JWT token de autenticação
    token = jwt.encode({
        'user_id': usuario.id,
        'exp': datetime.utcnow() + timedelta(hours=1)  # O token expira em 1 hora
    }, app.config['SECRET_KEY'], algorithm='HS256')

    # Se tudo estiver correto, responde com sucesso e o token JWT
    return jsonify({
        "mensagem": "Login bem-sucedido!",
        "token": token
    }), 200

# Registra o blueprint para a rota de autenticação
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        wait_for_db()  # Espera o banco de dados estar disponível
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True, host='0.0.0.0', port=5000)
