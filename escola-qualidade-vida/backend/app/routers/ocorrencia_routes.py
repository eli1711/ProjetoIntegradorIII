from flask import Blueprint, jsonify
from app.services.ocorrencia_service import listar_ocorrencias

ocorrencia_bp = Blueprint("ocorrencias", __name__, url_prefix="/ocorrencias")

@ocorrencia_bp.route("/", methods=["GET"])
def listar():
    ocorrencias = listar_ocorrencias()
    return jsonify([o.to_dict() for o in ocorrencias])
