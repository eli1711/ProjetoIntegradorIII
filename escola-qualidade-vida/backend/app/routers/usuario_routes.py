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

        # Permissões padrão por cargo
        if cargo == "administrador":
            permissoes = dict(criar_aluno=0, ocorrencias=0, relatorios=0,
                              historico=0, criar_usuario=0, gerenciamento_usuarios=0)
        elif cargo == "coordenador":
            permissoes = dict(criar_aluno=1, ocorrencias=1, relatorios=1,
                              historico=1, criar_usuario=1, gerenciamento_usuarios=1)
        else:  # analista
            permissoes = dict(criar_aluno=1, ocorrencias=1, relatorios=0,
                              historico=1, criar_usuario=0, gerenciamento_usuarios=0)

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=hash_senha,
            cargo=cargo,
            **permissoes
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Usuário criado com sucesso!'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Listar usuários
@usuario_bp.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = []
    for u in usuarios:
        resultado.append({
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'cargo': u.cargo,
            'permissoes': {
                "criar_aluno": u.criar_aluno,
                "ocorrencias": u.ocorrencias,
                "relatorios": u.relatorios,
                "historico": u.historico,
                "criar_usuario": u.criar_usuario,
                "gerenciamento_usuarios": u.gerenciamento_usuarios
            }
        })

    return jsonify({'usuarios': resultado}), 200


# Atualizar permissões
@usuario_bp.route("/usuarios/<int:user_id>/permissoes", methods=["PUT"])
def atualizar_permissoes(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado"}), 404

        permissoes = data.get("permissoes", {})

        usuario.criar_aluno = permissoes.get("criar_aluno", usuario.criar_aluno)
        usuario.ocorrencias = permissoes.get("ocorrencias", usuario.ocorrencias)
        usuario.relatorios = permissoes.get("relatorios", usuario.relatorios)
        usuario.historico = permissoes.get("historico", usuario.historico)
        usuario.criar_usuario = permissoes.get("criar_usuario", usuario.criar_usuario)
        usuario.gerenciamento_usuarios = permissoes.get("gerenciamento_usuarios", usuario.gerenciamento_usuarios)

        db.session.commit()

        return jsonify({"message": "Permissões atualizadas com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Obter permissões
@usuario_bp.route("/usuarios/<int:user_id>/permissoes", methods=["GET"])
def get_permissoes(user_id):
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify({
        "criar_aluno": usuario.criar_aluno,
        "ocorrencias": usuario.ocorrencias,
        "relatorios": usuario.relatorios,
        "historico": usuario.historico,
        "criar_usuario": usuario.criar_usuario,
        "gerenciamento_usuarios": usuario.gerenciamento_usuarios
    })
