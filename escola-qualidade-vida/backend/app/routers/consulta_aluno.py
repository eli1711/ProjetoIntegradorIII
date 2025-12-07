# app/routers/consulta_aluno.py
from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno, only_digits

consulta_aluno_bp = Blueprint("consulta_aluno", __name__, url_prefix="/alunos")


def _json_aluno_consulta(a: Aluno):
    turma = getattr(a, "turma_relacionada", None)
    curso = getattr(a, "curso_relacionado", None)

    return {
        "id": a.id,
        "cpf": getattr(a, "cpf", None),
        "matricula": getattr(a, "matricula", None),

        # o seu front usa aluno.nome no <h3>
        "nome": f"{getattr(a, 'nome', '')} {getattr(a, 'sobrenome', '')}".strip() or None,
        "nome_completo": getattr(a, "nome_completo", None),
        "nome_social": getattr(a, "nome_social", None),

        "foto": getattr(a, "foto", None),
        "foto_url": f"/uploads/{a.foto}" if getattr(a, "foto", None) else None,

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

        # seu front usa aluno.ocorrencias?.length (opcional)
        # só devolve se existir no model
        "ocorrencias": getattr(a, "ocorrencias", None),
    }


@consulta_aluno_bp.route("/buscar", methods=["GET"])
def buscar():
    cpf_raw = request.args.get("cpf")
    nome_raw = (request.args.get("nome") or "").strip()

    # 1) Prioridade: CPF
    if cpf_raw:
        cpf = only_digits(cpf_raw)
        if not cpf or len(cpf) != 11:
            return jsonify({"erro": "Informe o CPF com 11 dígitos"}), 400

        a = Aluno.query.filter_by(cpf=cpf).first()
        if not a:
            return jsonify([]), 200

        return jsonify([_json_aluno_consulta(a)]), 200

    # 2) Busca por nome (fallback)
    if nome_raw:
        q = Aluno.query.filter(Aluno.nome_completo.ilike(f"%{nome_raw}%")).limit(50).all()
        return jsonify([_json_aluno_consulta(a) for a in q]), 200

    return jsonify({"erro": "Informe cpf=... (11 dígitos) ou nome=..."}), 400
