from flask import Blueprint, jsonify
from app.services.turma_service import listar_turmas

turma_bp = Blueprint("turma", __name__, url_prefix="/turmas")

@turma_bp.route("/", methods=["GET"])
def listar_turmas():
    return jsonify(listar_turmas())
