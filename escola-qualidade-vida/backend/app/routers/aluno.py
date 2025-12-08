# app/routers/aluno.py
import os
import csv
import io
from datetime import datetime, date

from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.aluno import Aluno, only_digits
from app.models.responsavel import Responsavel
from app.models.turma import Turma
from app.models.curso import Curso

aluno_bp = Blueprint("aluno", __name__, url_prefix="/alunos")

# -------------------------
# Utilitários
# -------------------------
def str_to_bool(value):
    return str(value).strip().lower() in ["true", "1", "on", "t", "yes", "y", "sim"]

def parse_date(value):
    """
    Aceita:
      - YYYY-MM-DD
      - DD/MM/YYYY
    """
    if not value:
        return None
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None

def _norm(v: str) -> str:
    return (v or "").strip()

def _none_if_empty(v):
    v = _norm(v)
    return v if v != "" else None

def _calc_idade(dt: date | None) -> int | None:
    if not dt:
        return None
    hoje = date.today()
    return hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))

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
    turma = getattr(a, "turma_relacionada", None)
    curso = getattr(a, "curso_relacionado", None)

    return {
        "id": a.id,
        "cpf": a.cpf,
        "matricula": a.matricula,

        "nome": f"{getattr(a, 'nome', '')} {getattr(a, 'sobrenome', '')}".strip(),
        "nome_completo": getattr(a, "nome_completo", None),
        "nome_social": getattr(a, "nome_social", None),

        "foto": getattr(a, "foto", None),
        "foto_url": f"/uploads/{a.foto}" if getattr(a, "foto", None) else None,

        "curso": (curso.nome if curso else (getattr(a, "curso", None) or None)),
        "curso_id": getattr(a, "curso_id", None),

        "turma": (turma.nome if turma else (getattr(a, "turma", None) or None)),
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
    }

# Domínios válidos
_LINHAS_AT = {"CAI", "CT", "CST"}
_ESCOLAS = {"SESI", "SEDUC", "Nenhuma"}
_EMPREGADO = {"sim", "nao"}

# -------------------------
# CADASTRAR ALUNO COM CPF OBRIGATÓRIO
# -------------------------
@aluno_bp.route("/cadastrar", methods=["POST"])
def cadastrar_aluno_com_cpf():
    """
    Cadastra um novo aluno via formulário web com CPF OBRIGATÓRIO.
    Inclui nome_social sem quebrar se o model não tiver a coluna.
    """
    try:
        data = request.form
        current_app.logger.info(f"Dados recebidos para cadastro: {dict(data)}")

        # 1) CPF obrigatório
        cpf = data.get("cpf")
        if not cpf:
            return jsonify({"erro": "CPF é obrigatório"}), 400

        cpf_limpo = only_digits(cpf)
        if not cpf_limpo or len(cpf_limpo) != 11:
            return jsonify({"erro": "CPF deve conter 11 dígitos"}), 400

        if Aluno.query.filter_by(cpf=cpf_limpo).first():
            return jsonify({"erro": "CPF já cadastrado"}), 400

        # 2) Matrícula única
        matricula = _none_if_empty(data.get("matricula"))
        if matricula and Aluno.query.filter_by(matricula=matricula).first():
            return jsonify({"erro": "Matrícula já cadastrada"}), 400

        # 3) Nome completo / nome / sobrenome / nome_social
        nome_completo = _none_if_empty(data.get("nome_completo")) or ""
        nome = _none_if_empty(data.get("nome")) or ""
        sobrenome = _none_if_empty(data.get("sobrenome")) or ""
        nome_social = _none_if_empty(data.get("nome_social"))

        if nome_completo and not nome:
            partes = nome_completo.strip().split(" ", 1)
            nome = partes[0] if partes else ""
            sobrenome = partes[1] if len(partes) > 1 else ""
        elif nome and sobrenome and not nome_completo:
            nome_completo = f"{nome} {sobrenome}".strip()

        # 4) Campos principais
        cidade = _none_if_empty(data.get("cidade")) or ""
        bairro = _none_if_empty(data.get("bairro")) or ""
        rua = _none_if_empty(data.get("rua")) or ""
        telefone = only_digits(_none_if_empty(data.get("telefone"))) or None

        empregado = (_norm(data.get("empregado")) or "nao").lower()
        if empregado not in _EMPREGADO:
            return jsonify({"erro": "empregado deve ser 'sim' ou 'nao'."}), 400

        la = (_norm(data.get("linha_atendimento")) or "CAI").upper()
        if la not in _LINHAS_AT:
            return jsonify({"erro": "linha_atendimento deve ser CAI, CT ou CST."}), 400

        escola_integrada = _norm(data.get("escola_integrada") or "Nenhuma")
        if escola_integrada not in _ESCOLAS:
            return jsonify({"erro": "escola_integrada deve ser SESI, SEDUC ou Nenhuma."}), 400

        # Data nascimento + idade
        data_nascimento = parse_date(_none_if_empty(data.get("data_nascimento")))
        idade = None

        idade_raw = _none_if_empty(data.get("idade"))
        if idade_raw:
            try:
                idade = int(idade_raw)
            except Exception:
                return jsonify({"erro": "idade inválida (inteiro)."}), 400
        else:
            idade = _calc_idade(data_nascimento) if data_nascimento else None

        if idade is None:
            idade = 18

        # 5) Responsável (obrigatório se menor)
        responsavel_obj = None
        if idade < 18:
            r_nome = _none_if_empty(data.get("responsavel_nome_completo"))
            r_parentesco = _none_if_empty(data.get("responsavel_parentesco"))
            r_tel = only_digits(_none_if_empty(data.get("responsavel_telefone"))) or None

            if not (r_nome and r_parentesco and r_tel):
                return jsonify({
                    "erro": "Aluno menor de idade: campos do responsável são obrigatórios",
                    "faltando": [
                        c for c in ["responsavel_nome_completo", "responsavel_parentesco", "responsavel_telefone"]
                        if not _none_if_empty(data.get(c))
                    ]
                }), 400

            responsavel_obj = Responsavel(
                nome=r_nome,
                sobrenome="",
                parentesco=r_parentesco,
                telefone=r_tel,
                cidade=_none_if_empty(data.get("responsavel_cidade")),
                bairro=_none_if_empty(data.get("responsavel_bairro")),
                rua=_none_if_empty(data.get("responsavel_endereco")),
            )
            db.session.add(responsavel_obj)
            db.session.flush()

        # 6) Criar aluno (agora com nome_social)
        aluno = Aluno(
            nome=nome,
            sobrenome=sobrenome,
            nome_completo=nome_completo,
            nome_social=nome_social,

            cpf=cpf_limpo,
            matricula=matricula,

            cidade=cidade,
            bairro=bairro,
            rua=rua,
            telefone=telefone,

            idade=idade,
            empregado=empregado,

            data_nascimento=data_nascimento,
            linha_atendimento=la,
            escola_integrada=escola_integrada,

            curso=_none_if_empty(data.get("curso")),
            turma=_none_if_empty(data.get("turma")),

            mora_com_quem=_none_if_empty(data.get("mora_com_quem")),
            sobre_aluno=_none_if_empty(data.get("sobre_aluno")),
            data_inicio_curso=parse_date(_none_if_empty(data.get("data_inicio_curso"))),
            empresa_contratante=_none_if_empty(data.get("empresa_contratante")),
            pessoa_com_deficiencia=str_to_bool(_norm(data.get("pessoa_com_deficiencia"))),
            outras_informacoes=_none_if_empty(data.get("outras_informacoes")),

            responsavel_id=(responsavel_obj.id if responsavel_obj else None),
        )

        # Foto
        if "foto" in request.files and request.files["foto"].filename:
            foto = request.files["foto"]
            aluno.foto = _save_photo(foto, nome_completo or nome)

        aluno.normalize()
        db.session.add(aluno)
        db.session.commit()

        return jsonify({
            "mensagem": "Aluno cadastrado com sucesso!",
            "aluno_id": aluno.id,
            "cpf": aluno.cpf,
            "matricula": aluno.matricula,
            "nome_social": aluno.nome_social
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao cadastrar aluno: {str(e)}", exc_info=True)
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500


# -------------------------
# CONSULTAR ALUNO POR CPF
# -------------------------
@aluno_bp.route("/por-cpf/<string:cpf>", methods=["GET"])
def consultar_aluno_por_cpf(cpf):
    try:
        cpf_limpo = only_digits(cpf)
        if not cpf_limpo or len(cpf_limpo) != 11:
            return jsonify({"erro": "CPF inválido"}), 400

        aluno = Aluno.query.filter_by(cpf=cpf_limpo).first()
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404

        return jsonify(_json_aluno(aluno)), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao consultar aluno por CPF: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500


# -------------------------
# Saúde do blueprint
# -------------------------
@aluno_bp.route("/", methods=["GET"])
def listar_alunos():
    return jsonify({"mensagem": "Blueprint 'aluno_bp' ativo e funcionando corretamente!"}), 200


# -------------------------
# MODELO CSV (layout atual, com responsável e nome_social)
# -------------------------
@aluno_bp.route("/csv_modelo", methods=["GET"])
def csv_modelo_alunos():
    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        # Obrigatórios
        "matricula",
        "nome_completo",
        "cpf",
        "data_nascimento",
        "cidade",
        "bairro",
        "rua",
        "curso",
        "turma",
        "idade",
        "empregado",
        "linha_atendimento",
        "escola_integrada",

        # Opcionais
        "nome_social",
        "telefone",
        "mora_com_quem",
        "sobre_aluno",
        "data_inicio_curso",
        "empresa_contratante",
        "pessoa_com_deficiencia",
        "outras_informacoes",

        # Responsável (obrigatório se idade < 18)
        "responsavel_nome_completo",
        "responsavel_parentesco",
        "responsavel_telefone",
        "responsavel_cidade",
        "responsavel_bairro",
        "responsavel_endereco",

        # Compatibilidade (opcional)
        "curso_nome",
        "turma_nome",
        "curso_id",
        "turma_id",
    ]
    writer.writerow(headers)

    # Exemplo adulto
    writer.writerow([
        "MAT001",
        "João da Silva",
        "123.456.789-00",
        "2000-06-15",
        "Belo Horizonte",
        "Centro",
        "Rua das Flores, 123",
        "Informática Básica",
        "Turma A",
        "24",
        "sim",
        "CAI",
        "Nenhuma",
        "",  # nome_social
        "(31) 3333-4444",
        "Pais",
        "Aluno dedicado",
        "2025-02-01",
        "Empresa ABC",
        "false",
        "Observação qualquer",
        "", "", "", "", "", "",  # responsável vazio
        "Informática Básica", "Turma A", "", ""  # compat
    ])

    # Exemplo menor
    writer.writerow([
        "MAT002",
        "Maria Oliveira",
        "987.654.321-00",
        "20/03/2010",
        "Belo Horizonte",
        "Savassi",
        "Av. Brasil, 456",
        "Administração",
        "Turma B",
        "14",
        "nao",
        "CT",
        "SESI",
        "Maria (nome social)",
        "(31) 9999-8888",
        "Pais",
        "Boa aluna",
        "01/03/2025",
        "",
        "true",
        "Necessita adaptação",
        "Carlos Oliveira",
        "Pai",
        "(31) 98888-7777",
        "Belo Horizonte",
        "Savassi",
        "Av. Brasil, 456",
        "Administração", "Turma B", "", ""  # compat
    ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name="modelo_alunos.csv",
    )


# -------------------------
# IMPORTAR CSV (igual ao cadastro; sem foto)
# -------------------------
@aluno_bp.route("/importar_csv", methods=["POST"])
def importar_csv_alunos():
    """
    Importa um CSV e cria registros na tabela 'aluno'.
    Igual ao cadastro (sem foto). CPF obrigatório.
    Responsável obrigatório se idade < 18.
    Aceita data_nascimento e data_inicio_curso em YYYY-MM-DD ou DD/MM/YYYY.
    """
    if "arquivo" not in request.files or not request.files["arquivo"].filename:
        return jsonify({"erro": "Envie um arquivo CSV no campo 'arquivo'."}), 400

    f = request.files["arquivo"]
    try:
        content = f.read()
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        if not reader.fieldnames:
            return jsonify({"erro": "CSV sem cabeçalho."}), 400

        field_map = {(h or "").strip().lower(): h for h in reader.fieldnames}

        obrig = {
            "matricula", "nome_completo", "cpf", "data_nascimento",
            "cidade", "bairro", "rua",
            "curso", "turma",
            "empregado", "linha_atendimento", "escola_integrada",
        }

        missing_cols = obrig - set(field_map.keys())
        if missing_cols:
            return jsonify({"erro": f"CSV faltando colunas obrigatórias: {', '.join(sorted(missing_cols))}"}), 400

        sucesso = pulos = erros = 0
        rel = []

        def col(row, key: str):
            return row.get(field_map.get(key.lower(), key), "")

        for i, row in enumerate(reader, start=2):
            try:
                matricula = _none_if_empty(col(row, "matricula"))
                nome_completo = _none_if_empty(col(row, "nome_completo"))
                cpf_raw = _none_if_empty(col(row, "cpf"))
                data_nascimento_raw = _none_if_empty(col(row, "data_nascimento"))

                cidade = _none_if_empty(col(row, "cidade"))
                bairro = _none_if_empty(col(row, "bairro"))
                rua = _none_if_empty(col(row, "rua"))

                curso = _none_if_empty(col(row, "curso"))
                turma = _none_if_empty(col(row, "turma"))

                empregado = (_norm(col(row, "empregado")) or "nao").lower()
                la = (_norm(col(row, "linha_atendimento")) or "CAI").upper()
                escola_integrada = _none_if_empty(col(row, "escola_integrada")) or "Nenhuma"

                if not all([matricula, nome_completo, cpf_raw, data_nascimento_raw, cidade, bairro, rua, curso, turma]):
                    raise ValueError("Campos obrigatórios vazios.")

                if empregado not in _EMPREGADO:
                    raise ValueError("empregado deve ser 'sim' ou 'nao'.")
                if la not in _LINHAS_AT:
                    raise ValueError("linha_atendimento deve ser CAI, CT ou CST.")
                if escola_integrada not in _ESCOLAS:
                    raise ValueError("escola_integrada deve ser SESI, SEDUC ou Nenhuma.")

                cpf = only_digits(cpf_raw)
                if not cpf or len(cpf) != 11:
                    raise ValueError("CPF inválido (deve conter 11 dígitos).")
                if Aluno.query.filter_by(cpf=cpf).first():
                    pulos += 1
                    rel.append(f"[Linha {i}] CPF '{cpf_raw}' já cadastrado — pulado.")
                    continue

                if Aluno.query.filter_by(matricula=matricula).first():
                    pulos += 1
                    rel.append(f"[Linha {i}] Matrícula '{matricula}' já existe — pulado.")
                    continue

                data_nascimento = parse_date(data_nascimento_raw)
                if not data_nascimento:
                    raise ValueError("data_nascimento inválida (use YYYY-MM-DD ou DD/MM/YYYY).")

                idade_raw = _none_if_empty(col(row, "idade"))
                if idade_raw:
                    try:
                        idade = int(idade_raw)
                    except Exception:
                        raise ValueError("idade inválida (inteiro).")
                else:
                    idade = _calc_idade(data_nascimento)
                    if idade is None:
                        raise ValueError("Não foi possível calcular idade.")

                partes = nome_completo.strip().split(" ", 1)
                nome = partes[0] if partes else ""
                sobrenome = partes[1] if len(partes) > 1 else ""

                nome_social = _none_if_empty(col(row, "nome_social"))
                telefone = _none_if_empty(col(row, "telefone"))
                mora_com_quem = _none_if_empty(col(row, "mora_com_quem"))
                sobre_aluno = _none_if_empty(col(row, "sobre_aluno"))
                data_inicio_curso = parse_date(_none_if_empty(col(row, "data_inicio_curso")))
                empresa_contratante = _none_if_empty(col(row, "empresa_contratante"))
                pcd = str_to_bool(_norm(col(row, "pessoa_com_deficiencia")))
                outras_informacoes = _none_if_empty(col(row, "outras_informacoes"))

                responsavel_obj = None
                if idade < 18:
                    r_nome = _none_if_empty(col(row, "responsavel_nome_completo"))
                    r_parentesco = _none_if_empty(col(row, "responsavel_parentesco"))
                    r_tel = only_digits(_none_if_empty(col(row, "responsavel_telefone"))) or None
                    if not (r_nome and r_parentesco and r_tel):
                        pulos += 1
                        rel.append(f"[Linha {i}] Menor de idade sem dados obrigatórios do responsável — pulado.")
                        continue

                    responsavel_obj = Responsavel(
                        nome=r_nome,
                        sobrenome="",
                        parentesco=r_parentesco,
                        telefone=r_tel,
                        cidade=_none_if_empty(col(row, "responsavel_cidade")),
                        bairro=_none_if_empty(col(row, "responsavel_bairro")),
                        rua=_none_if_empty(col(row, "responsavel_endereco")),
                    )
                    db.session.add(responsavel_obj)
                    db.session.flush()

                # compat: tentar resolver curso/turma por id/nome (se vier)
                curso_nome = _none_if_empty(col(row, "curso_nome"))
                turma_nome = _none_if_empty(col(row, "turma_nome"))
                curso_id_raw = _none_if_empty(col(row, "curso_id"))
                turma_id_raw = _none_if_empty(col(row, "turma_id"))

                resolved_curso = None
                resolved_turma = None

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

                if resolved_curso and resolved_turma and resolved_turma.curso_id != resolved_curso.id:
                    rel.append(f"[Linha {i}] Aviso: turma_id não pertence ao curso_id — turma ignorada.")
                    resolved_turma = None

                if not resolved_curso and curso_nome:
                    resolved_curso = Curso.query.filter(Curso.nome.ilike(f"%{curso_nome}%")).first()
                    if not resolved_curso:
                        rel.append(f"[Linha {i}] Aviso: curso_nome '{curso_nome}' não encontrado — gravado apenas como texto.")

                if not resolved_turma and turma_nome:
                    q_turma = Turma.query
                    if resolved_curso:
                        q_turma = q_turma.filter(Turma.curso_id == resolved_curso.id)
                    resolved_turma = q_turma.filter(Turma.nome.ilike(f"%{turma_nome}%")).first()
                    if not resolved_turma:
                        rel.append(f"[Linha {i}] Aviso: turma_nome '{turma_nome}' não encontrada — gravada apenas como texto.")
                    if resolved_turma and not resolved_curso:
                        resolved_curso = resolved_turma.curso_relacionado

                if resolved_turma and resolved_curso and resolved_turma.curso_id != resolved_curso.id:
                    rel.append(f"[Linha {i}] Aviso: turma localizada não pertence ao curso localizado — turma ignorada.")
                    resolved_turma = None

                curso_id_val = resolved_curso.id if resolved_curso else None
                turma_id_val = resolved_turma.id if resolved_turma else None
                curso_texto = resolved_curso.nome if resolved_curso else (curso_nome or curso)
                turma_texto = resolved_turma.nome if resolved_turma else (turma_nome or turma)

                aluno = Aluno(
                    cpf=cpf,
                    matricula=matricula,

                    nome_completo=nome_completo,
                    nome=nome,
                    sobrenome=sobrenome,
                    nome_social=nome_social,

                    cidade=cidade,
                    bairro=bairro,
                    rua=rua,

                    idade=idade,
                    empregado=empregado,

                    telefone=only_digits(telefone) if telefone else None,
                    data_nascimento=data_nascimento,

                    linha_atendimento=la,
                    escola_integrada=escola_integrada,

                    curso=curso_texto,
                    turma=turma_texto,

                    data_inicio_curso=data_inicio_curso,
                    empresa_contratante=empresa_contratante,
                    mora_com_quem=mora_com_quem,
                    sobre_aluno=sobre_aluno,
                    pessoa_com_deficiencia=pcd,
                    outras_informacoes=outras_informacoes,

                    curso_id=curso_id_val,
                    turma_id=turma_id_val,

                    responsavel_id=(responsavel_obj.id if responsavel_obj else None),

                    foto=None,
                )

                aluno.normalize()
                db.session.add(aluno)
                db.session.commit()

                sucesso += 1
                rel.append(f"[Linha {i}] OK: {nome_completo} (CPF: {cpf}) - Nome social: {nome_social or 'Não informado'}.")

            except Exception as ex:
                db.session.rollback()
                erros += 1
                rel.append(f"[Linha {i}] ERRO: {str(ex)}")

        return jsonify({"sucesso": sucesso, "pulos": pulos, "erros": erros, "relatorio": rel}), 200

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

    # Campos que sempre existem
    for field in (
        "cidade", "bairro", "rua", "telefone", "empresa_contratante",
        "mora_com_quem", "sobre_aluno", "outras_informacoes", "curso", "turma"
    ):
        if field in data:
            setattr(aluno, field, _none_if_empty(data[field]))

    # nome_social
    if "nome_social" in data:
        aluno.nome_social = _none_if_empty(data["nome_social"])

    if "pessoa_com_deficiencia" in data:
        aluno.pessoa_com_deficiencia = bool(data["pessoa_com_deficiencia"])

    if "data_nascimento" in data:
        aluno.data_nascimento = parse_date(_none_if_empty(data["data_nascimento"]))
    if "data_inicio_curso" in data:
        aluno.data_inicio_curso = parse_date(_none_if_empty(data["data_inicio_curso"]))

    if "linha_atendimento" in data and data["linha_atendimento"]:
        la = str(data["linha_atendimento"]).upper()
        if la not in _LINHAS_AT:
            return jsonify({"erro": "linha_atendimento inválida."}), 400
        aluno.linha_atendimento = la

    if "escola_integrada" in data and data["escola_integrada"]:
        ei = data["escola_integrada"]
        if ei not in _ESCOLAS:
            return jsonify({"erro": "escola_integrada inválida."}), 400
        aluno.escola_integrada = ei

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
        resolved_curso = Curso.query.filter(Curso.nome.ilike(f"%{curso_nome}%")).first()

    if not resolved_turma and turma_nome:
        q_turma = Turma.query
        if resolved_curso:
            q_turma = q_turma.filter(Turma.curso_id == resolved_curso.id)
        resolved_turma = q_turma.filter(Turma.nome.ilike(f"%{turma_nome}%")).first()

    if resolved_turma and resolved_curso and resolved_turma.curso_id != resolved_curso.id:
        return jsonify({"erro": "A turma localizada não pertence ao curso localizado."}), 400

    if resolved_curso:
        aluno.curso_id = resolved_curso.id
        aluno.curso = resolved_curso.nome
    elif "curso_id" in data or "curso_nome" in data:
        if data.get("curso_id") in (None, "") and not curso_nome:
            aluno.curso_id = None

    if resolved_turma:
        aluno.turma_id = resolved_turma.id
        aluno.turma = resolved_turma.nome
    elif "turma_id" in data or "turma_nome" in data:
        if data.get("turma_id") in (None, "") and not turma_nome:
            aluno.turma_id = None

    aluno.normalize()
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
        novo_filename = _save_photo(file, aluno.nome_social or aluno.nome)

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
#verificar
@aluno_bp.route('/buscar', methods=['GET'])
def buscar_alunos():
    """Busca alunos por nome ou CPF"""
    nome = request.args.get('nome')
    cpf = request.args.get('cpf')
    
    try:
        query = Aluno.query
        
        if nome:
            query = query.filter(Aluno.nome.ilike(f'%{nome}%'))
        
        if cpf:
            # Remove formatação do CPF para busca
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            query = query.filter(Aluno.cpf == cpf_limpo)
        
        alunos = query.limit(20).all()
        
        resultado = []
        for aluno in alunos:
            aluno_dict = {
                'id': aluno.id,
                'nome': aluno.nome,
                'matricula': aluno.matricula,
                'cpf': aluno.cpf,  # Adicionar CPF na resposta
                'foto': aluno.foto,
                'foto_url': aluno.foto_url
            }
            resultado.append(aluno_dict)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'erro': 'Erro ao buscar alunos', 'detalhes': str(e)}), 500



# -------------------------
# BUSCAR (CPF ou NOME) - /alunos/buscar
# -------------------------
@aluno_bp.route("/buscar", methods=["GET"])
def buscar_aluno():
    cpf_raw = request.args.get("cpf")
    nome_raw = (request.args.get("nome") or "").strip()

    # 1) Por CPF (prioridade)
    if cpf_raw:
        cpf = only_digits(cpf_raw)
        if not cpf or len(cpf) != 11:
            return jsonify({"erro": "Informe o CPF com 11 dígitos"}), 400

        a = Aluno.query.filter_by(cpf=cpf).first()
        if not a:
            return jsonify([]), 200

        return jsonify([_json_aluno(a)]), 200

    # 2) Fallback por nome (incluindo nome_social)
    if nome_raw:
        q = Aluno.query.filter(
            (Aluno.nome_completo.ilike(f"%{nome_raw}%")) |
            (Aluno.nome.ilike(f"%{nome_raw}%")) |
            (Aluno.sobrenome.ilike(f"%{nome_raw}%")) |
            (Aluno.nome_social.ilike(f"%{nome_raw}%"))
        ).limit(50).all()
        return jsonify([_json_aluno(a) for a in q]), 200

    return jsonify({"erro": "Informe cpf=... (11 dígitos) ou nome=..."}), 400