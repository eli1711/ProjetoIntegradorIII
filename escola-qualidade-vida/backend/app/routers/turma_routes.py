from flask import Blueprint, request, jsonify
from datetime import datetime, date
from sqlalchemy import func

from app.extensions import db
from app.models.turma import Turma
from app.models.curso import Curso

turma_bp = Blueprint("turma", __name__, url_prefix="/turmas")

def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        return None

def _serialize_turma(t: Turma):
    return {
        "id": t.id,
        "nome": t.nome,
        "semestre": t.semestre,
        "curso_id": t.curso_id,
        "curso_nome": getattr(getattr(t, "curso", None), "nome", None),
        "data_inicio": t.data_inicio.isoformat() if t.data_inicio else None,
        "data_fim": t.data_fim.isoformat() if t.data_fim else None,
        "ativa": t.data_fim is None,
    }

def _get_or_create_curso(curso_id=None, curso_nome=None):
    if curso_id not in (None, "", "__novo__"):
        try:
            cid = int(curso_id)
        except ValueError:
            return None, ("curso_id inválido", 400)
        c = Curso.query.get(cid)
        if not c:
            return None, ("curso_id não encontrado", 400)
        return c, None

    # se veio por nome, cria/resolve
    if curso_nome:
        nome = str(curso_nome).strip()
        if not nome:
            return None, ("curso_nome vazio", 400)

        c = Curso.query.filter(func.lower(Curso.nome) == nome.lower()).first()
        if c:
            return c, None

        c = Curso(nome=nome)
        db.session.add(c)
        db.session.flush()
        return c, None

    return None, ("Informe curso_id ou curso_nome", 400)

@turma_bp.route("/", methods=["GET"])
def listar_turmas():
    """
    Parâmetros:
      - status=todas|ativas|finalizadas (default: todas)
      - curso_id=<int> (opcional)
    """
    status = (request.args.get("status") or "todas").strip().lower()
    curso_id = request.args.get("curso_id")

    query = Turma.query

    if status == "ativas":
        query = query.filter(Turma.data_fim.is_(None))
    elif status == "finalizadas":
        query = query.filter(Turma.data_fim.isnot(None))

    if curso_id:
        try:
            cid = int(curso_id)
            query = query.filter(Turma.curso_id == cid)
        except ValueError:
            return jsonify({"erro": "curso_id inválido"}), 400

    # ativas primeiro, depois finalizadas; dentro de cada, id desc
    turmas = query.order_by(Turma.data_fim.isnot(None), Turma.id.desc()).all()
    return jsonify([_serialize_turma(t) for t in turmas]), 200

@turma_bp.route("/por_curso", methods=["GET"])
def listar_turmas_por_curso():
    curso_id = request.args.get("curso_id")
    if not curso_id:
        return jsonify({"erro": "curso_id é obrigatório"}), 400
    try:
        cid = int(curso_id)
    except ValueError:
        return jsonify({"erro": "curso_id inválido"}), 400

    # ✅ incluir também as "mínimas" criadas no cadastro (ativas = data_fim is None)
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
    ✅ Agora aceita dois modos:

    1) Modo completo (igual antes):
       - nome, semestre, curso_id, data_inicio (obrigatórios)

    2) Modo mínimo (para ficar compatível com turmas criadas no cadastro/import):
       - nome + (curso_id OU curso_nome)
       (semestre e data_inicio serão preenchidos com defaults)
    """
    data = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict()

    nome = (data.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "nome é obrigatório"}), 400

    curso_id = data.get("curso_id")
    curso_nome = data.get("curso_nome") or data.get("curso")

    curso, err = _get_or_create_curso(curso_id=curso_id, curso_nome=curso_nome)
    if err:
        msg, code = err
        return jsonify({"erro": msg}), code

    # ✅ evita duplicar turma com mesmo nome no mesmo curso
    existente = Turma.query.filter(
        Turma.curso_id == curso.id,
        func.lower(Turma.nome) == nome.lower()
    ).first()
    if existente:
        return jsonify({"mensagem": "Turma já existe.", **_serialize_turma(existente)}), 200

    semestre = (data.get("semestre") or "").strip()
    data_inicio = _parse_date(data.get("data_inicio"))
    data_fim = _parse_date(data.get("data_fim"))

    # se for modo mínimo, preencher defaults
    if not semestre:
        semestre = "1"
    if not data_inicio:
        data_inicio = date.today()

    if semestre not in ("1", "2"):
        return jsonify({"erro": "semestre deve ser '1' ou '2'"}), 400

    if data_fim and data_fim < data_inicio:
        return jsonify({"erro": "data_fim não pode ser anterior à data_inicio"}), 400

    turma = Turma(
        nome=nome,
        semestre=semestre,
        curso_id=curso.id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    db.session.add(turma)
    db.session.commit()

    return jsonify({"mensagem": "Turma criada com sucesso!", **_serialize_turma(turma)}), 201

@turma_bp.route("/<int:turma_id>/finalizar", methods=["PATCH"])
def finalizar_turma(turma_id: int):
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

    # se data_inicio for None por algum motivo, não bloqueia
    if turma.data_inicio and fim < turma.data_inicio:
        return jsonify({"erro": "data_fim não pode ser anterior à data_inicio"}), 400

    turma.data_fim = fim
    db.session.commit()

    return jsonify({"mensagem": "Turma finalizada com sucesso!", **_serialize_turma(turma)}), 200
