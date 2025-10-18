from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.usuario import Usuario

usuario_bp = Blueprint('usuario_bp', __name__)

# Criar usuário
@usuario_bp.route('/api/criar_usuario', methods=['POST'])
def criar_usuario():
    try:
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        cargo = data.get('cargo')

        if not nome or not email or not senha or not cargo:
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400

        if cargo not in ['administrador', 'coordenador', 'analista']:
            return jsonify({'success': False, 'message': 'Cargo inválido'}), 400

        if Usuario.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Usuário já existe'}), 400

        hash_senha = generate_password_hash(senha)

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=hash_senha,
            cargo=cargo
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Listar usuários
@usuario_bp.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        usuarios = Usuario.query.all()
        resultado = []
        for u in usuarios:
            resultado.append({
                'id': u.id,
                'nome': u.nome,
                'email': u.email,
                'cargo': u.cargo
            })

        return jsonify({'usuarios': resultado}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500