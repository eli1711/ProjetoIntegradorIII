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
# ==== ADIÇÃO: atualização de aluno (PATCH /alunos/<id>) ====
from datetime import datetime

def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date() if s else None
    except Exception:
        return None

def _to_bool(v):
    return str(v).strip().lower() in {"true","1","t","y","yes","sim"}

@consulta_aluno_bp.route("/<int:aluno_id>", methods=["PATCH"])
def atualizar_aluno(aluno_id: int):
    a = Aluno.query.get(aluno_id)
    if not a:
        return jsonify({"erro": "Aluno não encontrado"}), 404

    data = request.get_json(silent=True) or {}

    # Campos simples
    for campo in ["cidade","bairro","rua","telefone","empresa_contratante",
                  "mora_com_quem","sobre_aluno","outras_informacoes"]:
        if campo in data:
            setattr(a, campo, (data[campo] or None))

    # Datas
    if "data_nascimento" in data:
        a.data_nascimento = _parse_date(data.get("data_nascimento"))
    if "data_inicio_curso" in data:
        a.data_inicio_curso = _parse_date(data.get("data_inicio_curso"))

    # Enums
    if "linha_atendimento" in data and data["linha_atendimento"]:
        if data["linha_atendimento"] not in {"CAI","CT","CST"}:
            return jsonify({"erro":"linha_atendimento inválida (CAI|CT|CST)"}), 400
        a.linha_atendimento = data["linha_atendimento"]

    if "escola_integrada" in data and data["escola_integrada"]:
        if data["escola_integrada"] not in {"SESI","SEDUC","Nenhuma"}:
            return jsonify({"erro":"escola_integrada inválida (SESI|SEDUC|Nenhuma)"}), 400
        a.escola_integrada = data["escola_integrada"]

    # Curso/Turma (checa coerência)
    from app.models.curso import Curso
    from app.models.turma import Turma

    novo_curso_id = data.get("curso_id")
    novo_turma_id = data.get("turma_id")

    if novo_curso_id is not None:
        try:
            novo_curso_id = int(novo_curso_id)
        except Exception:
            return jsonify({"erro":"curso_id inválido"}), 400
        if not Curso.query.get(novo_curso_id):
            return jsonify({"erro":"curso_id não encontrado"}), 400
        a.curso_id = novo_curso_id
        a.curso = str(novo_curso_id)  # mantém compatibilidade textual

    if novo_turma_id is not None:
        try:
            novo_turma_id = int(novo_turma_id)
        except Exception:
            return jsonify({"erro":"turma_id inválido"}), 400
        t = Turma.query.get(novo_turma_id)
        if not t:
            return jsonify({"erro":"turma_id não encontrado"}), 400
        # se curso_id foi alterado acima, ou mantém o atual, precisa bater
        curso_ref = a.curso_id or t.curso_id
        if t.curso_id != curso_ref:
            return jsonify({"erro":"turma_id não pertence ao curso_id informado"}), 400
        a.turma_id = novo_turma_id
        a.turma = str(novo_turma_id)  # compat textual

    # Boolean
    if "pessoa_com_deficiencia" in data:
        a.pessoa_com_deficiencia = _to_bool(data["pessoa_com_deficiencia"])

    db.session.commit()

    # Monta a resposta no mesmo formato do /buscar (para atualizar o card)
    turma = a.turma_relacionada
    curso = a.curso_relacionado
    foto_url = f"http://localhost:5000/uploads/{a.foto}" if a.foto else None

    out = {
        "id": a.id,
        "nome": f"{a.nome} {a.sobrenome}",
        "matricula": a.matricula,
        "foto_url": foto_url,
        "curso": (curso.nome if curso else (a.curso or None)),
        "turma": (turma.nome if turma else (a.turma or None)),
        "turma_nome": (turma.nome if turma else None),
        "turma_semestre": (turma.semestre if turma else None),
        "cidade": a.cidade or None,
        "bairro": a.bairro or None,
        "rua": a.rua or None,
        "telefone": a.telefone or None,
        "data_nascimento": a.data_nascimento.isoformat() if a.data_nascimento else None,
        "linha_atendimento": a.linha_atendimento,
        "escola_integrada": a.escola_integrada,
        "empresa_contratante": a.empresa_contratante or None,
        "data_inicio_curso": a.data_inicio_curso.isoformat() if a.data_inicio_curso else None,
        "mora_com_quem": a.mora_com_quem or None,
        "sobre_aluno": a.sobre_aluno or None,
        "pessoa_com_deficiencia": bool(a.pessoa_com_deficiencia),
        "outras_informacoes": a.outras_informacoes or None,
    }
    return jsonify(out), 200
