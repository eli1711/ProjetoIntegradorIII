from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados de login não fornecidos"}), 400

    email = data.get('email')
    senha = data.get('senha')
    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    # Verifica se usuário existe pelo email
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"erro": "Credenciais inválidas"}), 401

    # Verifica a senha usando hash
    if not check_password_hash(usuario.senha, senha):
        return jsonify({"erro": "Credenciais inválidas"}), 401

    # Gera token JWT de acesso (1 hora de expiração padrão)
    access_token = create_access_token(identity=usuario.id)
    return jsonify(access_token=access_token), 200
