from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.curso import Curso
from app.services.permission_service import auth_required, permission_required


curso_bp = Blueprint("curso", __name__, url_prefix="/cursos")


@curso_bp.route("/", methods=["GET"])
@auth_required()
def listar_cursos():
    cursos = Curso.query.order_by(Curso.nome.asc()).all()
    return jsonify([{"id": c.id, "nome": c.nome} for c in cursos]), 200


@curso_bp.route("/", methods=["POST"])
@permission_required("cadastro_turma")
def criar_curso():
    payload = request.get_json(silent=True) or {}
    nome = (payload.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "nome e obrigatorio"}), 400

    existente = Curso.query.filter(Curso.nome.ilike(nome)).first()
    if existente:
        return jsonify({"erro": "Ja existe um curso com esse nome.", "id": existente.id}), 409

    curso = Curso(nome=nome)
    db.session.add(curso)
    db.session.commit()

    return jsonify({"id": curso.id, "nome": curso.nome, "mensagem": "Curso criado com sucesso!"}), 201
