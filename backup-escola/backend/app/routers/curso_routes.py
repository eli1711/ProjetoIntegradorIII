from flask import Blueprint, jsonify, request
from app.services.curso_service import listar_cursos, criar_curso

curso_bp = Blueprint("curso", __name__, url_prefix="/cursos")

@curso_bp.route("/", methods=["GET"])
def listar():
    return jsonify(listar_cursos())

@curso_bp.route("/", methods=["POST"])
def criar():
    return jsonify(criar_curso(request.json)), 201
