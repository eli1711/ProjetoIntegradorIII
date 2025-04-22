from flask import Flask, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from app.models.usuario import Usuario


# Inicializa a aplicação e o banco
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'  # ou outro banco
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

    # Aqui poderia ser gerado um token JWT (opcional)
    return jsonify({"mensagem": "Login bem-sucedido!"}), 200

# Registra o blueprint
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas se ainda não existirem
    app.run(debug=True, host='0.0.0.0', port=5000)
