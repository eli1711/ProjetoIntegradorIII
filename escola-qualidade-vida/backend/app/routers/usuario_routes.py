# app/routers/usuario_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app import db
from app.models.usuario import Usuario

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/api/criar_usuario', methods=['POST'])
def criar_usuario():
    try:
        # Obtém os dados da requisição
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')

        # Valida se todos os campos foram fornecidos
        if not nome or not email or not senha:
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400

        # Verifica se o usuário já existe
        if Usuario.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Usuário já existe'}), 400

        # Criptografa a senha
        hash_senha = generate_password_hash(senha)

        # Cria um novo usuário
        novo_usuario = Usuario(nome=nome, email=email, senha=hash_senha)

        # Adiciona o usuário no banco de dados
        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
