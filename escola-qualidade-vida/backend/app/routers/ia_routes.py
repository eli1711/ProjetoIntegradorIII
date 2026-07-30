from flask import Blueprint, jsonify, request

from app.models.aluno import only_digits
from app.services.ia_aluno_service import analisar_alunos
from app.services.permission_service import permission_required


ia_bp = Blueprint("ia", __name__, url_prefix="/ia")


@ia_bp.get("/alunos/analise")
@permission_required("dashboard")
def analisar_turma_alunos():
    limit = request.args.get("limit", 30)
    cpf = request.args.get("cpf")

    if cpf:
        cpf_limpo = only_digits(cpf)
        if not cpf_limpo or len(cpf_limpo) != 11:
            return jsonify({"erro": "Informe o CPF com 11 digitos"}), 400

        result = analisar_alunos(limit=1, cpf=cpf_limpo)
        if result["total_analisado"] == 0:
            return jsonify({"erro": "Aluno nao encontrado para este CPF"}), 404
        return jsonify(result), 200

    return jsonify(analisar_alunos(limit=limit)), 200


@ia_bp.get("/alunos/<int:aluno_id>/analise")
@permission_required("dashboard")
def analisar_um_aluno(aluno_id):
    result = analisar_alunos(limit=1, aluno_id=aluno_id)
    if result["total_analisado"] == 0:
        return jsonify({"erro": "Aluno nao encontrado"}), 404
    return jsonify(result), 200
