import os
import time
import pymysql
from flask import Flask, Blueprint, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from sqlalchemy.exc import OperationalError

# Inicializa a aplicação
app = Flask(__name__, static_folder='static')  # Serve os arquivos estáticos a partir da pasta 'static'

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', 'password')}@"
    f"{os.environ.get('DB_HOST', 'mysql')}:{os.environ.get('DB_PORT', '3306')}/{os.environ.get('DB_NAME', 'escola_db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy
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

@app.route('/')
def home():
    return "Bem-vindo à página inicial!"


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({"erro": "E-mail ou senha inválidos"}), 401

    return jsonify({"mensagem": "Login bem-sucedido!"}), 200


# Serve arquivos estáticos (como HTML, CSS, JS)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({"erro": "E-mail ou senha inválidos"}), 401

    return jsonify({"mensagem": "Login bem-sucedido!"}), 200


# Registra o blueprint
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        wait_for_db()  # Espera o banco de dados estar disponível
    app.run(debug=True, host='0.0.0.0', port=5000)
