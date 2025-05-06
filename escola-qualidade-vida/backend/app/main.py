import os
import time
from flask import Flask, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_cors import CORS  # Importando CORS para permitir requisições de outras origens
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine

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

# Inicializando o SQLAlchemy
db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)  # senha com hash

# Blueprint de autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Função para esperar o banco de dados estar disponível
def wait_for_db():
    """Esperar até que o banco de dados esteja acessível."""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(db_uri)

    # Tenta conectar ao banco de dados até que a conexão seja bem-sucedida
    while True:
        try:
            with engine.connect() as connection:
                print("Conexão bem-sucedida com o banco de dados!")
                break
        except OperationalError:
            print("Banco de dados não disponível, tentando novamente em 2 segundos...")
            time.sleep(2)

@app.route('/')
def home():
    return "Bem-vindo à página inicial!"

@auth_bp.route('/login', methods=['POST'])
def login():
    """Rota de login que valida o e-mail e a senha do usuário."""
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    # Verifica se o e-mail e a senha foram fornecidos
    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    print(f"Recebendo login para o e-mail: {email}")  # Log para depuração

    # Verifica se o usuário existe no banco de dados
    usuario = Usuario.query.filter_by(email=email).first()

    # Se o usuário não for encontrado
    if not usuario:
        print(f"Usuário não encontrado para o e-mail: {email}")  # Log para depuração
        return jsonify({"erro": "E-mail ou senha inválidos"}), 401

    # Verifica se a senha fornecida é a mesma que a do banco de dados (com hash)
    if not check_password_hash(usuario.senha, senha):
        print(f"Senha incorreta para o usuário: {email}")  # Log para depuração
        return jsonify({"erro": "E-mail ou senha inválidos"}), 401

    # Se tudo estiver correto, responde com sucesso
    return jsonify({"mensagem": "Login bem-sucedido!"}), 200

# Registra o blueprint para a rota de autenticação
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        wait_for_db()  # Espera o banco de dados estar disponível
    app.run(debug=True, host='0.0.0.0', port=5000)
