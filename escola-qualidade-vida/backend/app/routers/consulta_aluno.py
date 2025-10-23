from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia

consulta_aluno_bp = Blueprint("consulta_aluno", __name__, url_prefix="/alunos")

@consulta_aluno_bp.route("/buscar", methods=["GET"])
def buscar_alunos_com_filtros():
    nome = request.args.get("nome", "").strip()

    try:
        query = Aluno.query.distinct(Aluno.id)
        if nome:
            query = query.filter(func.concat(Aluno.nome, " ", Aluno.sobrenome).ilike(f"%{nome}%"))

        alunos = query.all()
        resultado = []

        for aluno in alunos:
            deficiencia_descricao = "Não informada"
            if aluno.pessoa_com_deficiencia and aluno.outras_informacoes:
                if "Deficiência:" in aluno.outras_informacoes:
                    deficiencia_descricao = aluno.outras_informacoes.split("Deficiência:")[-1].strip()

            foto_url = f"http://localhost:5000/uploads/{aluno.foto}" if aluno.foto else None

            resultado.append({
                "id": aluno.id,
                "nome": f"{aluno.nome or ''} {aluno.sobrenome or ''}".strip(),
                "matricula": aluno.matricula or "Não informada",
                "curso": aluno.curso or (aluno.curso_relacionado.nome if aluno.curso_relacionado else "Não informado"),
                "turma": aluno.turma or "Não informada",
                "cidade": aluno.cidade or "Não informada",
                "bairro": aluno.bairro or "Não informado",
                "rua": aluno.rua or "Não informada",
                "telefone": aluno.telefone or "Não informado",
                "idade": aluno.idade or "Não informada",
                "data_nascimento": aluno.data_nascimento.isoformat() if aluno.data_nascimento else "Não informada",
                "linha_atendimento": aluno.linha_atendimento or "Não informada",
                "escola_integrada": aluno.escola_integrada or "Não informada",
                "empresa_contratante": aluno.empresa_contratante or "Não informada",
                "data_inicio_curso": aluno.data_inicio_curso.isoformat() if aluno.data_inicio_curso else "Não informada",
                "mora_com_quem": aluno.mora_com_quem or "Não informado",
                "sobre_aluno": aluno.sobre_aluno or "Não informado",
                "pessoa_com_deficiencia": "Sim" if aluno.pessoa_com_deficiencia else "Não",
                "deficiencia_descricao": deficiencia_descricao,
                "outras_informacoes": aluno.outras_informacoes or "Nenhuma",
                "foto_url": foto_url,
                "ocorrencias": [
                    {
                        "tipo": o.tipo,
                        "descricao": o.descricao,
                        "data_ocorrencia": o.data_ocorrencia.isoformat() if hasattr(o, "data_ocorrencia") and o.data_ocorrencia else "Sem data"
                    }
                    for o in getattr(aluno, "ocorrencias", [])
                ]
            })

        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        return jsonify({"erro": "Falha ao buscar alunos.", "detalhes": str(e)}), 500
