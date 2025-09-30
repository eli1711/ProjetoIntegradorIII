# usuarios_routes.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app import db
from app.models.usuario import Usuario
import json

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

        # Permissões padrão: administrador = bloqueado (false), coordenador = full (true)
        if cargo == "administrador":
            permissoes_default = {
                "cadastro-aluno": False,
                "ocorrencias": False,
                "relatorios": False,
                "historico": False
            }
        else:  # coordenador
            permissoes_default = {
                "cadastro-aluno": True,
                "ocorrencias": True,
                "relatorios": True,
                "historico": True
            }

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=hash_senha,
            cargo=cargo,
            permissoes=json.dumps(permissoes_default)
        )

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
    cargo_usuario = request.headers.get("Cargo")

    if cargo_usuario != "coordenador":
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    usuarios = Usuario.query.all()
    resultado = []
    for u in usuarios:
        if u.cargo == 'coordenador':
            # não mostrar coordenadores
            continue

        try:
            permissoes = json.loads(u.permissoes) if u.permissoes else {}
        except Exception:
            permissoes = {}

        resultado.append({
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'cargo': u.cargo,
            'permissoes': permissoes
        })

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

    # ajusta permissões ao trocar cargo
    if novo_cargo == 'administrador':
        permissoes_default = {
            "cadastro-aluno": False,
            "ocorrencias": False,
            "relatorios": False,
            "historico": False
        }
        usuario.permissoes = json.dumps(permissoes_default)
    else:  # coordenador
        permissoes_full = {
            "cadastro-aluno": True,
            "ocorrencias": True,
            "relatorios": True,
            "historico": True
        }
        usuario.permissoes = json.dumps(permissoes_full)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Cargo atualizado com sucesso'}), 200


# Atualizar permissões - CORRIGIDO
@usuario_bp.route("/usuarios/<int:user_id>/permissoes", methods=["PUT"])
def atualizar_permissoes(user_id):
    try:
        data = request.get_json()
        print(f"Recebendo permissões para usuário {user_id}:", data)  # DEBUG
        
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado"}), 404

        permissoes_obj = data.get("permissoes", {})
        print("Permissões recebidas:", permissoes_obj)  # DEBUG
        
        # Garante que todas as permissões estejam presentes
        permissoes_completas = {
            "cadastro-aluno": permissoes_obj.get("cadastro-aluno", False),
            "ocorrencias": permissoes_obj.get("ocorrencias", False),
            "relatorios": permissoes_obj.get("relatorios", False),
            "historico": permissoes_obj.get("historico", False)
        }
        
        usuario.permissoes = json.dumps(permissoes_completas)
        db.session.commit()
        
        print("Permissões salvas no banco:", usuario.permissoes)  # DEBUG
        
        return jsonify({"message": "Permissões atualizadas com sucesso"}), 200
        
    except Exception as e:
        print("Erro ao atualizar permissões:", str(e))
        return jsonify({"error": "Erro interno do servidor"}), 500


# Obter permissões - CORRIGIDO
@usuario_bp.route("/usuarios/<int:user_id>/permissoes", methods=["GET"])
def get_permissoes(user_id):
    try:
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado"}), 404

        print("Permissões no banco para usuário", user_id, ":", usuario.permissoes)  # DEBUG
        
        if usuario.permissoes:
            try:
                permissoes = json.loads(usuario.permissoes)
                print("Permissões parseadas:", permissoes)  # DEBUG
            except Exception as e:
                print("Erro ao fazer parse das permissões:", e)
                permissoes = {}
        else:
            permissoes = {}

        return jsonify(permissoes)
        
    except Exception as e:
        print("Erro ao obter permissões:", str(e))
        return jsonify({"error": "Erro interno do servidor"}), 500