# app/routers/aluno.py
import os
import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.empresa import Empresa
from app.models.turma import Turma
from app.models.curso import Curso

aluno_bp = Blueprint("aluno", __name__, url_prefix="/alunos")

# -------------------------
# Utilitários
# -------------------------
def str_to_bool(value):
    return str(value).lower() in ["true", "1", "on", "t", "yes", "y", "sim"]

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None
    except ValueError:
        return None

def _norm(v: str) -> str:
    return (v or "").strip()

def _none_if_empty(v):
    v = _norm(v)
    return v if v != "" else None

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def _save_photo(file_storage, desired_name_base: str) -> str:
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise ValueError("Extensão de imagem inválida. Use JPG, PNG, GIF ou WEBP.")

    base = secure_filename((desired_name_base or "aluno").lower())
    filename = f"{base}{ext}"
    dest = os.path.join(upload_dir, filename)

    i = 1
    while os.path.exists(dest):
        filename = f"{base}_{i}{ext}"
        dest = os.path.join(upload_dir, filename)
        i += 1

    file_storage.save(dest)
    current_app.logger.info(f"🖼️ Foto salva em: {dest}")
    return filename

def _json_aluno(a: Aluno):
    turma = a.turma_relacionada
    curso = a.curso_relacionado
    return {
        "id": a.id,
        "nome": f"{a.nome} {a.sobrenome}",
        "matricula": a.matricula,
        "foto": a.foto,
        "foto_url": f"/uploads/{a.foto}" if a.foto else None,
        "curso": (curso.nome if curso else (a.curso or None)),
        "curso_id": a.curso_id,
        "turma": (turma.nome if turma else (a.turma or None)),
        "turma_id": a.turma_id,
        "turma_nome": turma.nome if turma else None,
        "turma_semestre": turma.semestre if turma else None,
        "cidade": a.cidade, "bairro": a.bairro, "rua": a.rua,
        "telefone": a.telefone,
        "data_nascimento": a.data_nascimento.isoformat() if a.data_nascimento else None,
        "linha_atendimento": a.linha_atendimento,
        "escola_integrada": a.escola_integrada,
        "empresa_contratante": a.empresa_contratante,
        "data_inicio_curso": a.data_inicio_curso.isoformat() if a.data_inicio_curso else None,
        "mora_com_quem": a.mora_com_quem,
        "sobre_aluno": a.sobre_aluno,
        "pessoa_com_deficiencia": bool(a.pessoa_com_deficiencia),
        "outras_informacoes": a.outras_informacoes,
    }

# Domínios válidos
_LINHAS_AT = {"CAI", "CT", "CST"}
_ESCOLAS = {"SESI", "SEDUC", "Nenhuma"}
_EMPREGADO = {"sim", "nao"}

# -------------------------
# Saúde do blueprint
# -------------------------
@aluno_bp.route("/", methods=["GET"])
def listar_alunos():
    return jsonify({"mensagem": "Blueprint 'aluno_bp' ativo e funcionando corretamente!"}), 200

# -------------------------
# MODELO CSV (por NOME de curso/turma; IDs também aceitos)
# -------------------------
@aluno_bp.route("/csv_modelo", methods=["GET"])
def csv_modelo_alunos():
    """
    CSV de exemplo:
      - Usa 'curso_nome' e 'turma_nome' (opcionais). IDs também são aceitos como alternativa.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        # obrigatórios
        "nome","sobrenome","matricula","cidade","bairro","rua","idade",
        "linha_atendimento","escola_integrada",
        # nomes (preferenciais) - opcionais
        "curso_nome","turma_nome",
        # ids (alternativa) - opcionais
        "curso_id","turma_id",
        # outros opcionais
        "telefone","data_nascimento","empregado","mora_com_quem","sobre_aluno",
        "data_inicio_curso","empresa_contratante","pessoa_com_deficiencia","outras_informacoes"
    ]
    writer.writerow(headers)
    writer.writerow([
        "Ana","Silva","MAT001","Belo Horizonte","Centro","Rua A","16",
        "CAI","SESI",
        "Informática Básica","Turma 101",
        "","","(31) 99999-9999","2009-05-10","nao","","",
        "2025-02-01","","false",""
    ])
    writer.writerow([
        "Bruno","Souza","MAT002","BH","Savassi","Rua B","19",
        "CT","Nenhuma",
        "", "",  # curso_nome, turma_nome
        "2","12",  # usando IDs como alternativa
        "","2006-11-20","sim","Pais","Aluno destaque",
        "2025-03-01","Empresa X","true","Necessita adaptação de prova"
    ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name="modelo_alunos.csv",
    )

# -------------------------
# IMPORTAR CSV (aceita NOME ou ID; salva nomes; resolve FKs quando possível)
# -------------------------
@aluno_bp.route("/importar_csv", methods=["POST"])
def importar_csv_alunos():
    """
    Importa um CSV e cria registros na tabela 'aluno'.

    Obrigatórios por linha:
      - nome, sobrenome, matricula, cidade, bairro, rua, idade,
        linha_atendimento (CAI|CT|CST), escola_integrada (SESI|SEDUC|Nenhuma)

    Curso/Turma (opcionais):
      - Preferência por 'curso_nome' e 'turma_nome'. 
      - Alternativamente, aceita 'curso_id' e 'turma_id'.
      - IDs inexistentes NÃO barram a importação: são ignorados e FKs ficam NULL.
    """
    if "arquivo" not in request.files or not request.files["arquivo"].filename:
        return jsonify({"erro": "Envie um arquivo CSV no campo 'arquivo'."}), 400

    f = request.files["arquivo"]
    try:
        content = f.read()
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        obrig = {
            "nome","sobrenome","matricula","cidade","bairro","rua","idade",
            "linha_atendimento","escola_integrada"
        }

        if not reader.fieldnames:
            return jsonify({"erro": "CSV sem cabeçalho."}), 400

        field_map = {(h or "").strip(): h for h in reader.fieldnames}
        missing_cols = obrig - set(field_map.keys())
        if missing_cols:
            return jsonify({"erro": f"CSV faltando colunas obrigatórias: {', '.join(sorted(missing_cols))}"}), 400

        sucesso = pulos = erros = 0
        rel = []

        for i, row in enumerate(reader, start=2):
            try:
                def col(key):
                    return row.get(field_map.get(key, key))

                # -------- obrigatórios
                nome = _none_if_empty(col("nome"))
                sobrenome = _none_if_empty(col("sobrenome"))
                matricula = _none_if_empty(col("matricula"))
                cidade = _none_if_empty(col("cidade"))
                bairro = _none_if_empty(col("bairro"))
                rua = _none_if_empty(col("rua"))
                idade_raw = _none_if_empty(col("idade"))
                linha_atendimento = _none_if_empty(col("linha_atendimento"))
                escola_integrada = _none_if_empty(col("escola_integrada"))

                if not all([nome, sobrenome, matricula, cidade, bairro, rua, idade_raw,
                            linha_atendimento, escola_integrada]):
                    raise ValueError("Campos obrigatórios vazios.")

                try:
                    idade = int(idade_raw)
                except Exception:
                    raise ValueError("idade inválida (inteiro).")

                la = linha_atendimento.upper()
                if la not in _LINHAS_AT:
                    raise ValueError("linha_atendimento deve ser CAI, CT ou CST.")
                if escola_integrada not in _ESCOLAS:
                    raise ValueError("escola_integrada deve ser SESI, SEDUC ou Nenhuma.")

                # duplicidade de matrícula
                if Aluno.query.filter_by(matricula=matricula).first():
                    pulos += 1
                    rel.append(f"[Linha {i}] Matrícula '{matricula}' já existe — pulado.")
                    continue

                # -------- opcionais simples
                telefone = _none_if_empty(col("telefone"))
                empregado = (_norm(col("empregado")) or "nao").lower()
                if empregado not in _EMPREGADO:
                    raise ValueError("empregado deve ser 'sim' ou 'nao'.")

                mora_com_quem = _none_if_empty(col("mora_com_quem"))
                sobre_aluno = _none_if_empty(col("sobre_aluno"))
                data_nascimento = parse_date(_none_if_empty(col("data_nascimento")))
                data_inicio_curso = parse_date(_none_if_empty(col("data_inicio_curso")))
                empresa_contratante = _none_if_empty(col("empresa_contratante"))
                pcd = str_to_bool(_norm(col("pessoa_com_deficiencia")))
                outras_informacoes = _none_if_empty(col("outras_informacoes"))

                # -------- curso/turma por NOME ou ID (suave)
                curso_nome = _none_if_empty(col("curso_nome"))
                turma_nome = _none_if_empty(col("turma_nome"))
                curso_id_raw = _none_if_empty(col("curso_id"))
                turma_id_raw = _none_if_empty(col("turma_id"))

                resolved_curso = None
                resolved_turma = None

                # Tenta por ID, mas NÃO erra se não achar
                if curso_id_raw:
                    try:
                        resolved_curso = Curso.query.get(int(curso_id_raw))
                        if not resolved_curso:
                            rel.append(f"[Linha {i}] Aviso: curso_id '{curso_id_raw}' não encontrado — ignorado.")
                    except Exception:
                        rel.append(f"[Linha {i}] Aviso: curso_id inválido — ignorado.")

                if turma_id_raw:
                    try:
                        resolved_turma = Turma.query.get(int(turma_id_raw))
                        if not resolved_turma:
                            rel.append(f"[Linha {i}] Aviso: turma_id '{turma_id_raw}' não encontrado — ignorado.")
                    except Exception:
                        rel.append(f"[Linha {i}] Aviso: turma_id inválido — ignorado.")

                # Coerência entre IDs se ambos existem; se incoerente, ignora a turma
                if resolved_curso and resolved_turma and resolved_turma.curso_id != resolved_curso.id:
                    rel.append(f"[Linha {i}] Aviso: turma_id não pertence ao curso_id — turma ignorada.")
                    resolved_turma = None

                # Tenta resolver por NOME quando ainda não resolvido
                if not resolved_curso and curso_nome:
                    resolved_curso = Curso.query.filter(Curso.nome.ilike(curso_nome)).first()
                    if not resolved_curso:
                        rel.append(f"[Linha {i}] Aviso: curso_nome '{curso_nome}' não encontrado — gravado apenas como texto.")

                if not resolved_turma and turma_nome:
                    q_turma = Turma.query
                    if resolved_curso:
                        q_turma = q_turma.filter(Turma.curso_id == resolved_curso.id)
                    resolved_turma = q_turma.filter(Turma.nome.ilike(turma_nome)).first()
                    if not resolved_turma:
                        rel.append(f"[Linha {i}] Aviso: turma_nome '{turma_nome}' não encontrada — gravada apenas como texto.")
                    # se achou turma e não havia curso, infere
                    if resolved_turma and not resolved_curso:
                        resolved_curso = resolved_turma.curso_relacionado

                # Coerência final (se nome resolveu turma mas curso não bate)
                if resolved_turma and resolved_curso and resolved_turma.curso_id != resolved_curso.id:
                    rel.append(f"[Linha {i}] Aviso: turma localizada não pertence ao curso localizado — turma ignorada.")
                    resolved_turma = None

                curso_id_val = resolved_curso.id if resolved_curso else None
                turma_id_val = resolved_turma.id if resolved_turma else None
                curso_texto = (resolved_curso.nome if resolved_curso else curso_nome)
                turma_texto = (resolved_turma.nome if resolved_turma else turma_nome)

                aluno = Aluno(
                    nome=nome,
                    sobrenome=sobrenome,
                    matricula=matricula,
                    cidade=cidade,
                    bairro=bairro,
                    rua=rua,
                    idade=idade,
                    empregado=empregado,
                    mora_com_quem=mora_com_quem,
                    sobre_aluno=sobre_aluno,
                    foto=None,
                    telefone=telefone,
                    data_nascimento=data_nascimento,
                    linha_atendimento=la,
                    curso=curso_texto,     # salva nomes quando houver
                    turma=turma_texto,     # salva nomes quando houver
                    data_inicio_curso=data_inicio_curso,
                    empresa_contratante=empresa_contratante,
                    escola_integrada=escola_integrada,
                    pessoa_com_deficiencia=pcd,
                    outras_informacoes=outras_informacoes,
                    curso_id=curso_id_val, # FKs somente se resolvidos
                    turma_id=turma_id_val
                )

                db.session.add(aluno)
                db.session.commit()

                sucesso += 1
                rel.append(f"[Linha {i}] OK: {nome} {sobrenome} (matrícula {matricula}).")

            except Exception as ex:
                db.session.rollback()
                erros += 1
                rel.append(f"[Linha {i}] ERRO: {str(ex)}")

        return jsonify({
            "sucesso": sucesso,
            "pulos": pulos,
            "erros": erros,
            "relatorio": rel
        }), 200

    except UnicodeDecodeError:
        return jsonify({"erro": "Não foi possível ler o arquivo. Use CSV UTF-8."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Falha ao processar CSV.", "detalhes": str(e)}), 500

# -------------------------
# EDITAR ALUNO (dados)
# -------------------------
@aluno_bp.route("/<int:aluno_id>", methods=["PATCH"])
def editar_aluno(aluno_id: int):
    aluno = Aluno.query.get_or_404(aluno_id)
    data = request.get_json(silent=True) or {}

    # Atualiza apenas campos enviados; strings vazias viram None
    for field in ("cidade", "bairro", "rua", "telefone", "empresa_contratante",
                  "mora_com_quem", "sobre_aluno", "outras_informacoes", "curso", "turma"):
        if field in data:
            setattr(aluno, field, _none_if_empty(data[field]))

    if "pessoa_com_deficiencia" in data:
        aluno.pessoa_com_deficiencia = bool(data["pessoa_com_deficiencia"])

    if "data_nascimento" in data:
        aluno.data_nascimento = parse_date(_none_if_empty(data["data_nascimento"]))
    if "data_inicio_curso" in data:
        aluno.data_inicio_curso = parse_date(_none_if_empty(data["data_inicio_curso"]))

    if "linha_atendimento" in data and data["linha_atendimento"]:
        la = data["linha_atendimento"]
        if la not in _LINHAS_AT:
            return jsonify({"erro": "linha_atendimento inválida."}), 400
        aluno.linha_atendimento = la

    if "escola_integrada" in data and data["escola_integrada"]:
        ei = data["escola_integrada"]
        if ei not in _ESCOLAS:
            return jsonify({"erro": "escola_integrada inválida."}), 400
        aluno.escola_integrada = ei

    # Se vierem curso_nome/turma_nome na edição, também tento resolver os FKs (opcional)
    curso_nome = _none_if_empty(data.get("curso_nome"))
    turma_nome = _none_if_empty(data.get("turma_nome"))
    curso_id = data.get("curso_id", None)
    turma_id = data.get("turma_id", None)

    resolved_curso = None
    resolved_turma = None

    if turma_id not in (None, ""):
        t = Turma.query.get(int(turma_id))
        if not t:
            return jsonify({"erro": "turma_id não encontrado."}), 400
        resolved_turma = t
    if curso_id not in (None, ""):
        c = Curso.query.get(int(curso_id))
        if not c:
            return jsonify({"erro": "curso_id não encontrado."}), 400
        resolved_curso = c

    if not resolved_curso and curso_nome:
        resolved_curso = Curso.query.filter(Curso.nome.ilike(curso_nome)).first()
    if not resolved_turma and turma_nome:
        q_turma = Turma.query
        if resolved_curso:
            q_turma = q_turma.filter(Turma.curso_id == resolved_curso.id)
        resolved_turma = q_turma.filter(Turma.nome.ilike(turma_nome)).first()

    if resolved_turma and resolved_curso and resolved_turma.curso_id != resolved_curso.id:
        return jsonify({"erro": "A turma localizada não pertence ao curso localizado."}), 400

    if resolved_curso:
        aluno.curso_id = resolved_curso.id
        aluno.curso = resolved_curso.nome
    elif "curso_id" in data or "curso_nome" in data:
        # Se a edição explicitamente limpou
        if data.get("curso_id") in (None, "") and not curso_nome:
            aluno.curso_id = None

    if resolved_turma:
        aluno.turma_id = resolved_turma.id
        aluno.turma = resolved_turma.nome
    elif "turma_id" in data or "turma_nome" in data:
        if data.get("turma_id") in (None, "") and not turma_nome:
            aluno.turma_id = None

    db.session.commit()
    return jsonify(_json_aluno(aluno)), 200

# -------------------------
# TROCAR FOTO DO ALUNO
# -------------------------
@aluno_bp.route("/<int:aluno_id>/foto", methods=["PUT"])
def trocar_foto(aluno_id: int):
    aluno = Aluno.query.get_or_404(aluno_id)

    if "foto" not in request.files or not request.files["foto"].filename:
        return jsonify({"erro": "Envie a imagem no campo 'foto'."}), 400

    file = request.files["foto"]
    try:
        novo_filename = _save_photo(file, aluno.nome)
        # remove antiga (se existir)
        if aluno.foto:
            try:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], aluno.foto)
                if os.path.exists(old_path):
                    os.remove(old_path)
                    current_app.logger.info(f"🗑️ Foto antiga removida: {old_path}")
            except Exception:
                pass

        aluno.foto = novo_filename
        db.session.commit()

        return jsonify({
            "mensagem": "Foto atualizada com sucesso!",
            "aluno_id": aluno.id,
            "foto": aluno.foto,
            "foto_url": f"/uploads/{aluno.foto}"
        }), 200

    except ValueError as ve:
        return jsonify({"erro": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro ao trocar foto do aluno")
        return jsonify({"erro": "Falha ao atualizar foto.", "detalhes": str(e)}), 500
