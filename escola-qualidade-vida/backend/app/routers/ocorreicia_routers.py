from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ocorrencia_service import listar_ocorrencias
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno
from app import db

ocorrencia_bp = Blueprint("ocorrencias", __name__, url_prefix="/ocorrencias")

@ocorrencia_bp.route("/", methods=["GET"])
@jwt_required()
def listar_ocorrencias_route():
    """Retorna a lista de ocorrências registradas."""
    ocorrencias = listar_ocorrencias()
    return jsonify(ocorrencias), 200

@ocorrencia_bp.route("/registrar", methods=["POST"])
@jwt_required()
def registrar_ocorrencia():
    """Registra uma nova ocorrência disciplinar."""
    try:
        data = request.get_json()
        aluno_id = data.get('aluno_id')
        tipo = data.get('tipo')
        descricao = data.get('descricao')
        usuario_id = get_jwt_identity()  # ID do usuário logado (autor da ocorrência)

        if not aluno_id or not tipo or not descricao:
            return jsonify({"erro": "Dados incompletos!"}), 400

        # Verifica se o aluno existe
        aluno = Aluno.query.get(aluno_id)
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado!"}), 404

        # Cria a nova ocorrência e salva
        nova_ocorrencia = Ocorrencia(aluno_id=aluno_id, tipo=tipo, descricao=descricao, usuario_id=usuario_id)
        db.session.add(nova_ocorrencia)
        db.session.commit()
        return jsonify({"mensagem": "Ocorrência registrada com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500
