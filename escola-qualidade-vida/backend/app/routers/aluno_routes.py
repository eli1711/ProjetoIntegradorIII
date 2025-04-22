from flask import Blueprint, jsonify
from app.services.aluno_service import listar_alunos

aluno_bp = Blueprint("alunos", __name__, url_prefix="/alunos")

@aluno_bp.route("/", methods=["GET"])
def listar():
    alunos = listar_alunos()
    return jsonify(alunos)
