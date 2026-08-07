from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.models.aluno import Aluno, only_digits
from app.models.curso import Curso
from app.models.ocorrencia import Ocorrencia
from app.models.turma import Turma
from app.services.permission_service import auth_required


consulta_aluno_bp = Blueprint("consulta_aluno", __name__, url_prefix="/alunos")


def _json_aluno_consulta(a: Aluno):
    turma = getattr(a, "turma_relacionada", None)
    curso = getattr(a, "curso_relacionado", None)

    return {
        "id": a.id,
        "cpf": getattr(a, "cpf", None),
        "matricula": getattr(a, "matricula", None),
        "nome": f"{getattr(a, 'nome', '')} {getattr(a, 'sobrenome', '')}".strip() or None,
        "nome_completo": getattr(a, "nome_completo", None),
        "nome_social": getattr(a, "nome_social", None),
        "foto": getattr(a, "foto", None),
        "foto_url": f"/files/uploads/{a.foto}" if getattr(a, "foto", None) else None,
        "curso": (curso.nome if curso else getattr(a, "curso", None)),
        "curso_id": getattr(a, "curso_id", None),
        "turma": (turma.nome if turma else getattr(a, "turma", None)),
        "turma_id": getattr(a, "turma_id", None),
        "turma_nome": turma.nome if turma else None,
        "turma_semestre": getattr(turma, "semestre", None) if turma else None,
        "cidade": getattr(a, "cidade", None),
        "bairro": getattr(a, "bairro", None),
        "rua": getattr(a, "rua", None),
        "telefone": getattr(a, "telefone", None),
        "data_nascimento": a.data_nascimento.isoformat() if getattr(a, "data_nascimento", None) else None,
        "linha_atendimento": getattr(a, "linha_atendimento", None),
        "escola_integrada": getattr(a, "escola_integrada", None),
        "empresa_contratante": getattr(a, "empresa_contratante", None),
        "data_inicio_curso": a.data_inicio_curso.isoformat() if getattr(a, "data_inicio_curso", None) else None,
        "mora_com_quem": getattr(a, "mora_com_quem", None),
        "sobre_aluno": getattr(a, "sobre_aluno", None),
        "pessoa_com_deficiencia": bool(getattr(a, "pessoa_com_deficiencia", False)),
        "outras_informacoes": getattr(a, "outras_informacoes", None),
        "ocorrencias": [oc.to_dict() for oc in (getattr(a, "ocorrencias", None) or [])],
    }


def _bounded_limit(default=100, maximum=200):
    try:
        value = int(request.args.get("limit", default))
    except (TypeError, ValueError):
        value = default
    return max(1, min(value, maximum))


@consulta_aluno_bp.route("/buscar", methods=["GET"])
@auth_required()
def buscar():
    cpf_raw = request.args.get("cpf")
    nome_raw = (request.args.get("nome") or "").strip()
    curso_raw = (request.args.get("curso") or "").strip()
    turma_raw = (request.args.get("turma") or "").strip()
    tipo_ocorrencia = (request.args.get("ocorrencia") or request.args.get("tipo") or "").strip()

    if cpf_raw:
        cpf = only_digits(cpf_raw)
        if not cpf or len(cpf) != 11:
            return jsonify({"erro": "Informe o CPF com 11 digitos"}), 400

        aluno = Aluno.query.filter_by(cpf=cpf).first()
        return jsonify([_json_aluno_consulta(aluno)] if aluno else []), 200

    query = Aluno.query.outerjoin(Curso, Aluno.curso_id == Curso.id).outerjoin(Turma, Aluno.turma_id == Turma.id)

    if nome_raw:
        like_nome = f"%{nome_raw}%"
        digitos = only_digits(nome_raw)
        condicoes_nome = [
            Aluno.nome_completo.ilike(like_nome),
            Aluno.nome.ilike(like_nome),
            Aluno.sobrenome.ilike(like_nome),
            Aluno.nome_social.ilike(like_nome),
            Aluno.matricula.ilike(like_nome),
        ]
        if digitos:
            condicoes_nome.append(Aluno.cpf.ilike(f"%{digitos}%"))
            condicoes_nome.append(Aluno.matricula.ilike(f"%{digitos}%"))
        query = query.filter(or_(*condicoes_nome))

    if curso_raw:
        like_curso = f"%{curso_raw}%"
        query = query.filter(or_(Curso.nome.ilike(like_curso), Aluno.curso.ilike(like_curso)))

    if turma_raw:
        like_turma = f"%{turma_raw}%"
        query = query.filter(or_(Turma.nome.ilike(like_turma), Aluno.turma.ilike(like_turma)))

    if tipo_ocorrencia:
        query = query.join(Ocorrencia, Ocorrencia.aluno_id == Aluno.id).filter(Ocorrencia.tipo == tipo_ocorrencia)

    alunos = query.distinct().order_by(Aluno.id.desc()).limit(_bounded_limit()).all()
    return jsonify([_json_aluno_consulta(aluno) for aluno in alunos]), 200
