import os
import csv
import io
from datetime import datetime, date

from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from app.extensions import db
from app.models.aluno import Aluno, only_digits
from app.models.responsavel import Responsavel
from app.models.turma import Turma
from app.models.curso import Curso
from app.services.aluno_registration_service import (
    StudentRegistrationError,
    register_student_from_form,
)
from app.services.permission_service import permission_required

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
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

def _save_photo(file_storage, desired_name_base: str) -> str:
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise ValueError("Extensão de imagem inválida. Use JPG, PNG, GIF ou WEBP.")
    if file_storage.mimetype and file_storage.mimetype not in ALLOWED_IMAGE_MIMES:
        raise ValueError("Tipo de imagem invalido. Use JPG, PNG, GIF ou WEBP.")

    base = secure_filename((desired_name_base or "aluno").lower())
    filename = f"{base}{ext}"
    dest = os.path.join(upload_dir, filename)

    i = 1
    while os.path.exists(dest):
        filename = f"{base}_{i}{ext}"
        dest = os.path.join(upload_dir, filename)
        i += 1

    file_storage.save(dest)
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
        "foto_url": f"/files/uploads/{a.foto}" if getattr(a, "foto", None) else None,

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
# AUTO-CREATE: Curso e Turma
# -------------------------
def _get_or_create_curso(nome_curso: str | None) -> Curso | None:
    nome_curso = _none_if_empty(nome_curso)
    if not nome_curso:
        return None

    # tenta achar igual
    c = Curso.query.filter(Curso.nome.ilike(nome_curso)).first()
    if c:
        return c

    # cria
    c = Curso(nome=nome_curso)
    db.session.add(c)
    db.session.flush()  # pega id sem commit
    return c

def _get_or_create_turma(nome_turma: str | None, curso: Curso | None) -> Turma | None:
    nome_turma = _none_if_empty(nome_turma)
    if not nome_turma or not curso:
        return None

    # procura turma com mesmo nome dentro do curso
    t = Turma.query.filter(
        Turma.curso_id == curso.id,
        Turma.nome.ilike(nome_turma),
    ).first()
    if t:
        return t

    # cria turma "mínima" ignorando semestre/início/fim informados
    # (ajuste se sua model permitir NULL nesses campos)
    t = Turma(
        nome=nome_turma,
        curso_id=curso.id,
        semestre="1",            # default
        data_inicio=date.today(), # default
        data_fim=None,
    )
    db.session.add(t)
    db.session.flush()
    return t

def _resolve_existing_curso(curso_id: str | None, nome_curso: str | None):
    curso_id = _none_if_empty(curso_id)
    if curso_id:
        try:
            cid = int(curso_id)
        except ValueError:
            return None, "Curso invalido."

        curso = Curso.query.get(cid)
        if not curso:
            return None, "Curso nao encontrado. Selecione um curso ja cadastrado."
        return curso, None

    nome_curso = _none_if_empty(nome_curso)
    if nome_curso:
        curso = Curso.query.filter(Curso.nome.ilike(nome_curso)).first()
        if curso:
            return curso, None

    return None, "Selecione um curso ja cadastrado."

def _resolve_existing_turma(turma_id: str | None, nome_turma: str | None, curso: Curso | None):
    if not curso:
        return None, "Selecione um curso ja cadastrado antes da turma."

    turma_id = _none_if_empty(turma_id)
    if turma_id:
        try:
            tid = int(turma_id)
        except ValueError:
            return None, "Turma invalida."

        turma = Turma.query.get(tid)
        if not turma:
            return None, "Turma nao encontrada. Selecione uma turma ja cadastrada."
        if turma.curso_id != curso.id:
            return None, "A turma selecionada nao pertence ao curso escolhido."
        return turma, None

    nome_turma = _none_if_empty(nome_turma)
    if nome_turma:
        turma = Turma.query.filter(
            Turma.curso_id == curso.id,
            Turma.nome.ilike(nome_turma),
        ).first()
        if turma:
            return turma, None

    return None, "Selecione uma turma ja cadastrada para o curso escolhido."

# -------------------------
# CADASTRAR ALUNO COM CPF OBRIGATÓRIO
# -------------------------
@aluno_bp.route("/cadastrar", methods=["POST"])
@permission_required("cadastro_aluno")
def cadastrar_aluno_com_cpf():
    """
    Cadastra um novo aluno via formulário web com CPF OBRIGATÓRIO.
    Associa apenas Curso/Turma ja cadastrados.
    """
    try:
        aluno = register_student_from_form(
            request.form,
            request.files,
            require_existing_course=True,
        )

        return jsonify({
            "mensagem": "Aluno cadastrado com sucesso!",
            "aluno_id": aluno.id,
            "cpf": aluno.cpf,
            "matricula": aluno.matricula,
            "nome_social": aluno.nome_social,
            "curso_id": aluno.curso_id,
            "turma_id": aluno.turma_id,
        }), 201

    except StudentRegistrationError as e:
        db.session.rollback()
        return jsonify(e.to_payload()), e.status_code
    except Exception:
        db.session.rollback()
        current_app.logger.error("Erro ao cadastrar aluno", exc_info=True)
        return jsonify({"erro": "Erro interno ao cadastrar aluno"}), 500

# -------------------------
# MODELO CSV
# -------------------------
@aluno_bp.route("/csv_modelo", methods=["GET"])
def csv_modelo_alunos():
    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
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
        "nome_social",
        "telefone",
        "mora_com_quem",
        "sobre_aluno",
        "data_inicio_curso",
        "empresa_contratante",
        "pessoa_com_deficiencia",
        "outras_informacoes",
        "responsavel_nome_completo",
        "responsavel_parentesco",
        "responsavel_telefone",
        "responsavel_cidade",
        "responsavel_bairro",
        "responsavel_endereco",
    ]
    writer.writerow(headers)

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
        "",
        "(31) 3333-4444",
        "Pais",
        "Aluno dedicado",
        "2025-02-01",
        "Empresa ABC",
        "false",
        "Observação qualquer",
        "", "", "", "", "", "",
    ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name="modelo_alunos.csv",
    )

# -------------------------
# IMPORTAR CSV (cria Curso/Turma automaticamente)
# -------------------------
@aluno_bp.route("/importar_csv", methods=["POST"])
@permission_required("importar_alunos")
def importar_csv_alunos():
    """
    Importa um CSV e cria registros na tabela 'aluno'.
    CPF obrigatório.
    Responsável obrigatório se idade < 18.
    Cria Curso/Turma automaticamente quando 'curso' e 'turma' vierem preenchidos.
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

                curso_txt = _none_if_empty(col(row, "curso"))
                turma_txt = _none_if_empty(col(row, "turma"))

                empregado = (_norm(col(row, "empregado")) or "nao").lower()
                la = (_norm(col(row, "linha_atendimento")) or "CAI").upper()
                escola_integrada = _none_if_empty(col(row, "escola_integrada")) or "Nenhuma"

                if not all([matricula, nome_completo, cpf_raw, data_nascimento_raw, cidade, bairro, rua, curso_txt, turma_txt]):
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
                        nome_completo=r_nome,
                        parentesco=r_parentesco,
                        telefone=r_tel,
                        endereco=_none_if_empty(col(row, "responsavel_endereco")),
                        cep=only_digits(_none_if_empty(col(row, "responsavel_cep"))) or None,
                        bairro=_none_if_empty(col(row, "responsavel_bairro")),
                        municipio=_none_if_empty(col(row, "responsavel_cidade")),
                    )
                    db.session.add(responsavel_obj)
                    db.session.flush()

                # ✅ Cria curso e turma automaticamente
                resolved_curso = _get_or_create_curso(curso_txt)
                resolved_turma = _get_or_create_turma(turma_txt, resolved_curso)

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

                    curso=(resolved_curso.nome if resolved_curso else curso_txt),
                    turma=(resolved_turma.nome if resolved_turma else turma_txt),
                    curso_id=(resolved_curso.id if resolved_curso else None),
                    turma_id=(resolved_turma.id if resolved_turma else None),

                    data_inicio_curso=data_inicio_curso,
                    empresa_contratante=empresa_contratante,
                    mora_com_quem=mora_com_quem,
                    sobre_aluno=sobre_aluno,
                    pessoa_com_deficiencia=pcd,
                    outras_informacoes=outras_informacoes,

                    responsavel_id=(responsavel_obj.id if responsavel_obj else None),
                    foto=None,
                )

                aluno.normalize()
                db.session.add(aluno)
                db.session.commit()

                sucesso += 1
                rel.append(f"[Linha {i}] OK: {nome_completo} (CPF: {cpf}) - Turma criada/associada: {turma_txt}.")

            except Exception as ex:
                db.session.rollback()
                erros += 1
                rel.append(f"[Linha {i}] ERRO: {str(ex)}")

        return jsonify({"sucesso": sucesso, "pulos": pulos, "erros": erros, "relatorio": rel}), 200

    except UnicodeDecodeError:
        return jsonify({"erro": "Não foi possível ler o arquivo. Use CSV UTF-8."}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Falha ao processar CSV: %s", e, exc_info=True)
        return jsonify({"erro": "Falha ao processar CSV."}), 500


# -------------------------
# ATUALIZAR ALUNO / FOTO
# -------------------------
@aluno_bp.route("/<int:aluno_id>", methods=["PUT", "PATCH"])
@permission_required("cadastro_aluno")
def atualizar_aluno(aluno_id: int):
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({"erro": "Aluno nao encontrado"}), 404

    data = request.get_json(silent=True) or {}

    try:
        if "cpf" in data:
            cpf = only_digits(data.get("cpf"))
            if not cpf or len(cpf) != 11:
                return jsonify({"erro": "CPF deve conter 11 digitos"}), 400
            existente = Aluno.query.filter(Aluno.cpf == cpf, Aluno.id != aluno.id).first()
            if existente:
                return jsonify({"erro": "CPF ja cadastrado para outro aluno"}), 409
            aluno.cpf = cpf

        if "matricula" in data:
            matricula = _none_if_empty(data.get("matricula"))
            if not matricula:
                return jsonify({"erro": "matricula nao pode ficar vazia"}), 400
            existente = Aluno.query.filter(Aluno.matricula == matricula, Aluno.id != aluno.id).first()
            if existente:
                return jsonify({"erro": "Matricula ja cadastrada para outro aluno"}), 409
            aluno.matricula = matricula

        for campo in [
            "nome_completo", "nome", "sobrenome", "nome_social", "cidade",
            "bairro", "rua", "empregado", "linha_atendimento", "escola_integrada",
            "mora_com_quem", "sobre_aluno", "empresa_contratante", "outras_informacoes",
        ]:
            if campo in data:
                setattr(aluno, campo, _none_if_empty(data.get(campo)))

        if "telefone" in data:
            aluno.telefone = only_digits(_none_if_empty(data.get("telefone"))) or None

        if "idade" in data and data.get("idade") not in (None, ""):
            try:
                aluno.idade = int(data.get("idade"))
            except (TypeError, ValueError):
                return jsonify({"erro": "idade invalida"}), 400

        if "data_nascimento" in data:
            aluno.data_nascimento = parse_date(_none_if_empty(data.get("data_nascimento")))

        if "data_inicio_curso" in data:
            aluno.data_inicio_curso = parse_date(_none_if_empty(data.get("data_inicio_curso")))

        if "pessoa_com_deficiencia" in data:
            aluno.pessoa_com_deficiencia = str_to_bool(data.get("pessoa_com_deficiencia"))

        curso = None
        if data.get("curso_id"):
            curso = Curso.query.get(int(data["curso_id"]))
            if not curso:
                return jsonify({"erro": "curso_id nao encontrado"}), 400
            aluno.curso_id = curso.id
            aluno.curso = curso.nome
        elif "curso" in data:
            curso = _get_or_create_curso(data.get("curso"))
            aluno.curso_id = curso.id if curso else None
            aluno.curso = curso.nome if curso else _none_if_empty(data.get("curso"))

        if data.get("turma_id"):
            turma = Turma.query.get(int(data["turma_id"]))
            if not turma:
                return jsonify({"erro": "turma_id nao encontrada"}), 400
            aluno.turma_id = turma.id
            aluno.turma = turma.nome
        elif "turma" in data:
            if not curso and aluno.curso_id:
                curso = Curso.query.get(aluno.curso_id)
            turma = _get_or_create_turma(data.get("turma"), curso) if curso else None
            aluno.turma_id = turma.id if turma else None
            aluno.turma = turma.nome if turma else _none_if_empty(data.get("turma"))

        aluno.normalize()
        db.session.commit()
        aluno_json = _json_aluno(aluno)
        return jsonify({"mensagem": "Aluno atualizado com sucesso!", "aluno": aluno_json, **aluno_json}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao atualizar aluno", exc_info=True)
        return jsonify({"erro": "Erro interno ao atualizar aluno"}), 500


@aluno_bp.route("/<int:aluno_id>/foto", methods=["PUT"])
@permission_required("cadastro_aluno")
def atualizar_foto_aluno(aluno_id: int):
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({"erro": "Aluno nao encontrado"}), 404

    if "foto" not in request.files or not request.files["foto"].filename:
        return jsonify({"erro": "Envie uma foto no campo 'foto'."}), 400

    try:
        aluno.foto = _save_photo(request.files["foto"], aluno.nome_completo or aluno.nome)
        db.session.commit()
        return jsonify({
            "mensagem": "Foto atualizada com sucesso!",
            "foto": aluno.foto,
            "foto_url": f"/files/uploads/{aluno.foto}",
        }), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao atualizar foto", exc_info=True)
        return jsonify({"erro": "Erro interno ao atualizar foto"}), 500


# -------------------------
# DASHBOARD COMPATIBILITY
# -------------------------
@aluno_bp.route("/dashboard_data", methods=["GET"])
@permission_required("dashboard")
def dashboard_data():
    from app.routers.dashboard import dashboard as dashboard_view

    return dashboard_view()

