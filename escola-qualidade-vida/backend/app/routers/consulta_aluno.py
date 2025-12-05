# app/routers/consulta_aluno.py
from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno, only_digits

consulta_aluno_bp = Blueprint("consulta_aluno", __name__, url_prefix="/alunos")

@consulta_aluno_bp.route("/buscar", methods=["GET"])
def buscar():
    cpf_raw = request.args.get("cpf")
    nome_raw = (request.args.get("nome") or "").strip()

    # 1) Prioridade: CPF (mantém exatamente o comportamento que você quer)
    if cpf_raw:
        cpf = only_digits(cpf_raw)
        if not cpf or len(cpf) != 11:
            return jsonify({"erro": "Informe o CPF com 11 dígitos"}), 400

        a = Aluno.query.filter_by(cpf=cpf).first()
        if not a:
            return jsonify([]), 200

        resp = getattr(a, "responsavel", None)

        return jsonify([{
            "id": a.id,
            "nome_completo": getattr(a, "nome_completo", None),
            "nome_social": getattr(a, "nome_social", None),
            "cpf": a.cpf,
            "matricula": a.matricula,

            "data_nascimento": a.data_nascimento.isoformat() if a.data_nascimento else None,

            "endereco": getattr(a, "endereco", None),
            "cep": getattr(a, "cep", None),
            "bairro": getattr(a, "bairro", None),
            "municipio": getattr(a, "municipio", None),

            "telefone": getattr(a, "telefone", None),
            "celular": getattr(a, "celular", None),

            "curso": getattr(a, "curso", None),
            "tipo_curso": getattr(a, "tipo_curso", None),
            "turma": getattr(a, "turma", None),

            "empresa_aprendizagem": getattr(a, "empresa_aprendizagem", None),
            "cnpj_empresa": getattr(a, "cnpj_empresa", None),

            "pne": bool(getattr(a, "pne", False)),
            "pne_descricao": getattr(a, "pne_descricao", None),

            "parceria_novo_ensino_medio": getattr(a, "parceria_novo_ensino_medio", None),

            "foto_url": f"/uploads/{a.foto}" if getattr(a, "foto", None) else None,

            "responsavel": ({
                "nome_completo": resp.nome_completo,
                "parentesco": resp.parentesco,
                "telefone": resp.telefone,
                "endereco": resp.endereco,
                "cep": resp.cep,
                "bairro": resp.bairro,
                "municipio": resp.municipio,
            } if resp else None)
        }]), 200

    # 2) Fallback: busca por nome (para não ficar 400 quando o front chama ?nome=...)
    if nome_raw:
        # busca parcial, case-insensitive
        q = Aluno.query.filter(Aluno.nome_completo.ilike(f"%{nome_raw}%")).limit(50).all()

        # mantém o padrão do front: lista
        return jsonify([{
            "id": a.id,
            "nome_completo": getattr(a, "nome_completo", None),
            "nome_social": getattr(a, "nome_social", None),
            "cpf": getattr(a, "cpf", None),
            "matricula": getattr(a, "matricula", None),
            "foto_url": f"/uploads/{a.foto}" if getattr(a, "foto", None) else None,
        } for a in q]), 200

    # 3) Se não vier cpf nem nome
    return jsonify({"erro": "Informe cpf=... (11 dígitos) ou nome=..."}), 400
