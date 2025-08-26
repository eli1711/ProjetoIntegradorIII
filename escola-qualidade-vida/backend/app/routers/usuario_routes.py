from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.usuario import Usuario

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    try:
        data = request.get_json() or {}
        nome = (data.get('nome') or '').strip()
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''
        cargo = (data.get('cargo') or '').strip()

        if not nome or not email or not senha or not cargo:
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400

        if cargo not in ('administrador', 'coordenador'):
            return jsonify({'success': False, 'message': 'Cargo inválido'}), 400

        if Usuario.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Usuário já existe'}), 400

        hash_senha = generate_password_hash(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=hash_senha, cargo=cargo)

        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'}), 201

    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'success': False, 'message': 'Erro ao criar usuário.', 'detail': str(e)}), 500
