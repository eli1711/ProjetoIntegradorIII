from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app import db
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

        if cargo not in ['administrador', 'coordenador']:
            return jsonify({'success': False, 'message': 'Cargo inválido'}), 400

        if Usuario.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Usuário já existe'}), 400

        hash_senha = generate_password_hash(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=hash_senha, cargo=cargo)

        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Rota de teste
@usuario_bp.route('/api/test', methods=['GET', 'POST'])
def test_route():
    return jsonify({'message': 'Rota de teste funcionando!', 'method': request.method}), 200


# Listar usuários (somente coordenador pode ver)
@usuario_bp.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    cargo_usuario = request.headers.get("Cargo")  # <- Simples checagem

    if cargo_usuario != "coordenador":
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    usuarios = Usuario.query.all()
    resultado = [
        {
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'cargo': u.cargo,
            'permissoes': u.permissoes or {}  # 🔹 ADICIONADO: retorna permissões
        }
        for u in usuarios if u.cargo != 'coordenador'  # 🔹 Não mostra coordenadores
    ]
    return jsonify({'usuarios': resultado}), 200


# Atualizar cargo
@usuario_bp.route('/api/usuarios/<int:user_id>', methods=['PUT'])
def atualizar_usuario(user_id):
    data = request.get_json()
    novo_cargo = data.get('cargo')

    if novo_cargo not in ['coordenador', 'administrador']:
        return jsonify({'success': False, 'message': 'Cargo inválido'}), 400

    usuario = Usuario.query.get(user_id)
    if not usuario:
        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

    usuario.cargo = novo_cargo
    db.session.commit()
    return jsonify({'success': True, 'message': 'Cargo atualizado com sucesso'}), 200


# Atualizar permissões
@usuario_bp.route("/usuarios/<int:user_id>/permissoes", methods=["PUT"])
def atualizar_permissoes(user_id):
    data = request.json
    usuario = Usuario.query.get(user_id)

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    usuario.permissoes = data.get("permissoes", {})
    db.session.commit()

    return jsonify({"message": "Permissões atualizadas com sucesso"}), 200


# Obter permissões
@usuario_bp.route("/usuarios/<int:user_id>/permissoes", methods=["GET"])
def get_permissoes(user_id):
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(usuario.permissoes or {})