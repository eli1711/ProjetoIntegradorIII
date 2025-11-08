# app/routers/consulta_aluno.py  (ou onde está a rota /alunos/buscar)
from datetime import date
from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno
from app.models.turma import Turma
from app.models.curso import Curso
from app.extensions import db

consulta_aluno_bp = Blueprint("consulta_aluno", __name__)

def _calc_idade(dt):
    if not dt:
        return None
    hoje = date.today()
    # idade precisa considerar mês/dia
    return hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))

@consulta_aluno_bp.route("/buscar", methods=["GET"])
def buscar():
    nome = (request.args.get("nome") or "").strip()
    q = Aluno.query
    if nome:
        q = q.filter(
            db.func.concat(Aluno.nome, " ", Aluno.sobrenome).ilike(f"%{nome}%")
        )

    alunos = q.order_by(Aluno.id.desc()).all()
    out = []
    for a in alunos:
        # relações (podem ser None)
        turma = a.turma_relacionada
        curso = a.curso_relacionado

        # idade correta
        idade = _calc_idade(a.data_nascimento)

        # telefone: None quando vazio -> o front mostra "Não informado"
        telefone = a.telefone or None

        # pessoa_com_deficiencia: manter boolean
        pcd = bool(a.pessoa_com_deficiencia)

        # “curso” preferindo o nome da tabela cursos; se não houver, cai no texto legado
        curso_nome = curso.nome if curso else (a.curso or None)

        # turma: nome e semestre se existir FK
        turma_nome = turma.nome if turma else (a.turma or None)
        turma_semestre = turma.semestre if turma else None

        # foto pública (se existir arquivo gravado)
        foto_url = f"http://localhost:5000/uploads/{a.foto}" if a.foto else None

        # Se você guarda “Deficiência: …” dentro de outras_informacoes, extraia opcionalmente:
        def_descr = None
        if a.outras_informacoes:
            prefix = "Deficiência:"
            txt = a.outras_informacoes.strip()
            if txt.startswith(prefix):
                def_descr = txt[len(prefix):].strip()

        out.append({
            "id": a.id,
            "nome": f"{a.nome} {a.sobrenome}",
            "matricula": a.matricula,
            "foto_url": foto_url,
            "curso": curso_nome,
            "turma": turma_nome,
            "turma_semestre": turma_semestre,
            "cidade": a.cidade or None,
            "bairro": a.bairro or None,
            "rua": a.rua or None,
            "telefone": telefone,                      # <- None quando vazio
            "idade": idade,                            # <- calculado corretamente
            "data_nascimento": a.data_nascimento.isoformat() if a.data_nascimento else None,
            "linha_atendimento": a.linha_atendimento,
            "escola_integrada": a.escola_integrada,
            "empresa_contratante": a.empresa_contratante or None,
            "data_inicio_curso": a.data_inicio_curso.isoformat() if a.data_inicio_curso else None,
            "mora_com_quem": a.mora_com_quem or None,
            "sobre_aluno": a.sobre_aluno or None,
            "outras_informacoes": a.outras_informacoes or None,
            "pessoa_com_deficiencia": pcd,            # <- boolean (True/False)
            "deficiencia_descricao": def_descr,       # <- só quando detectado
            # se quiser, traga as ocorrências já “enxutas”
            "ocorrencias": [
                {
                    "tipo": oc.tipo,
                    "descricao": oc.descricao,
                    "data_ocorrencia": oc.data_ocorrencia.isoformat() if oc.data_ocorrencia else None
                }
                for oc in getattr(a, "ocorrencias", []) or []
            ],
        })
    return jsonify(out), 200
