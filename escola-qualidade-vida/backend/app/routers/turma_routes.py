# app/routers/turma_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from app.extensions import db
from app.models.turma import Turma
from app.models.curso import Curso  # ajuste o import conforme seu projeto

turma_bp = Blueprint("turma", __name__, url_prefix="/turmas")


def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        return None


@turma_bp.route("/", methods=["GET"])
def listar_turmas():
    """
    Lista turmas.
    Parâmetros opcionais:
      - status=ativas|todas (default: ativas -> data_fim IS NULL)
      - curso_id=<int>
    """
    status = request.args.get("status", "ativas").strip().lower()
    curso_id = request.args.get("curso_id")

    query = Turma.query
    if status == "ativas":
        query = query.filter(Turma.data_fim.is_(None))

    if curso_id:
        try:
            cid = int(curso_id)
            query = query.filter(Turma.curso_id == cid)
        except ValueError:
            return jsonify({"erro": "curso_id inválido"}), 400

    turmas = query.order_by(Turma.id.desc()).all()
    out = []
    for t in turmas:
        out.append({
            "id": t.id,
            "nome": t.nome,
            "semestre": t.semestre,
            "curso_id": t.curso_id,
            "data_inicio": t.data_inicio.isoformat() if t.data_inicio else None,
            "data_fim": t.data_fim.isoformat() if t.data_fim else None,
            "ativa": t.data_fim is None,
            "curso_nome": getattr(getattr(t, "curso", None), "nome", None),
        })
    return jsonify(out), 200


@turma_bp.route("/por_curso", methods=["GET"])
def listar_turmas_por_curso():
    """
    Lista APENAS turmas ativas de um curso específico (para preencher selects).
    Ex: /turmas/por_curso?curso_id=3
    """
    curso_id = request.args.get("curso_id")
    if not curso_id:
        return jsonify({"erro": "curso_id é obrigatório"}), 400
    try:
        cid = int(curso_id)
    except ValueError:
        return jsonify({"erro": "curso_id inválido"}), 400

    turmas = Turma.query.filter(
        Turma.curso_id == cid,
        Turma.data_fim.is_(None)
    ).order_by(Turma.nome.asc()).all()

    return jsonify([
        {
            "id": t.id,
            "nome": t.nome,
            "semestre": t.semestre,
            "data_inicio": t.data_inicio.isoformat() if t.data_inicio else None
        } for t in turmas
    ]), 200


@turma_bp.route("/", methods=["POST"])
def criar_turma():
    """
    Cria uma turma. Aceita JSON, form-data (multipart/urlencoded) ou querystring.
    Campos obrigatórios: nome, semestre ('1'|'2'), curso_id, data_inicio (YYYY-MM-DD)
    Opcional: data_fim (YYYY-MM-DD)
    """
    data = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict()

    obrigatorios = ["nome", "semestre", "curso_id", "data_inicio"]
    if not all(data.get(k) for k in obrigatorios):
        return jsonify({"erro": "Campos obrigatórios: nome, semestre, curso_id, data_inicio"}), 400

    semestre = str(data.get("semestre")).strip()
    if semestre not in ("1", "2"):
        return jsonify({"erro": "semestre deve ser '1' ou '2'"}), 400

    # curso_id precisa existir
    try:
        curso_id = int(data.get("curso_id"))
    except (TypeError, ValueError):
        return jsonify({"erro": "curso_id inválido"}), 400

    if not Curso.query.get(curso_id):
        return jsonify({"erro": "curso_id não encontrado"}), 400

    data_inicio = _parse_date(data.get("data_inicio"))
    data_fim = _parse_date(data.get("data_fim"))
    if not data_inicio:
        return jsonify({"erro": "data_inicio inválida (use YYYY-MM-DD)"}), 400
    if data_fim and data_fim < data_inicio:
        return jsonify({"erro": "data_fim não pode ser anterior à data_inicio"}), 400

    turma = Turma(
        nome=data["nome"].strip(),
        semestre=semestre,
        curso_id=curso_id,
        data_inicio=data_inicio,
        data_fim=data_fim,  # normalmente None (preencher só ao encerrar)
    )
    db.session.add(turma)
    db.session.commit()

    return jsonify({"mensagem": "Turma criada com sucesso!", "id": turma.id}), 201


@turma_bp.route("/<int:turma_id>/finalizar", methods=["PATCH"])
def finalizar_turma(turma_id: int):
    """
    Finaliza uma turma (define data_fim).
    Corpo aceito (opcional): {"data_fim": "YYYY-MM-DD"}.
    Se não enviar, usa a data de hoje.
    """
    turma = Turma.query.get(turma_id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404
    if turma.data_fim is not None:
        return jsonify({"erro": "Turma já está finalizada"}), 400

    payload = request.get_json(silent=True) or {}
    data_fim_str = payload.get("data_fim")
    if data_fim_str:
        fim = _parse_date(data_fim_str)
        if not fim:
            return jsonify({"erro": "data_fim inválida (use YYYY-MM-DD)"}), 400
    else:
        fim = date.today()

    if fim < turma.data_inicio:
        return jsonify({"erro": "data_fim não pode ser anterior à data_inicio"}), 400

    turma.data_fim = fim
    db.session.commit()

    return jsonify({
        "mensagem": "Turma finalizada com sucesso!",
        "id": turma.id,
        "data_fim": turma.data_fim.isoformat()
    }), 200
