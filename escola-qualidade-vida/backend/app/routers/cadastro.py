# app/routers/cadastro.py
import os
from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.aluno import Aluno, only_digits
from app.models.responsavel import Responsavel

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        return None

def _calc_idade(dt: date | None) -> int | None:
    if not dt:
        return None
    hoje = date.today()
    return hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))

def str_to_bool(value):
    return str(value).strip().lower() in ["true", "1", "on", "t", "yes", "y", "sim"]

def _norm(v):
    return (v or "").strip()

def _none_if_empty(v):
    v = _norm(v)
    return v if v else None

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
    return filename

@cadastro_bp.route("/alunos", methods=["POST"])
def cadastrar_aluno():
    form = request.form

    current_app.logger.info(f"FORM_KEYS={list(form.keys())}")
    current_app.logger.info(f"FILES_KEYS={list(request.files.keys())}")

    # ========= CAMPOS OBRIGATÓRIOS (conforme seu FORM_KEYS atual) =========
    obrigatorios = [
        "matricula", "nome_completo", "cpf", "data_nascimento",
        "endereco", "cep", "bairro", "municipio",
        "curso", "tipo_curso", "turma",
    ]
    faltando = [c for c in obrigatorios if not _norm(form.get(c))]
    if faltando:
        return jsonify({"erro": "Campos obrigatórios não preenchidos", "faltando": faltando}), 400

    # ========= NORMALIZA / VALIDA CPF e CEP =========
    cpf = only_digits(form.get("cpf"))
    if not cpf or len(cpf) != 11:
        return jsonify({"erro": "CPF inválido (informe 11 dígitos)"}), 400

    cep = only_digits(form.get("cep"))
    if not cep or len(cep) != 8:
        return jsonify({"erro": "CEP inválido (informe 8 dígitos)"}), 400

    # ========= DATA NASCIMENTO + IDADE (calculada) =========
    data_nasc = _parse_date(form.get("data_nascimento"))
    if not data_nasc:
        return jsonify({"erro": "data_nascimento inválida (use YYYY-MM-DD)"}), 400

    idade = _calc_idade(data_nasc)
    if idade is None:
        return jsonify({"erro": "Não foi possível calcular a idade."}), 400

    # ========= PNE / EMPRESA =========
    pne = str_to_bool(form.get("pne"))
    pne_descricao = _none_if_empty(form.get("pne_descricao"))

    empresa = _none_if_empty(form.get("empresa_aprendizagem"))
    cnpj = only_digits(form.get("cnpj_empresa"))
    if cnpj and len(cnpj) != 14:
        return jsonify({"erro": "CNPJ inválido (informe 14 dígitos)"}), 400
    if cnpj and not empresa:
        return jsonify({"erro": "Informe o nome da empresa ao preencher CNPJ"}), 400
    if empresa and not cnpj:
        return jsonify({"erro": "Informe o CNPJ ao preencher o nome da empresa"}), 400

    # ========= RESPONSÁVEL (obrigatório se menor) =========
    responsavel_obj = None
    if idade < 18:
        resp_obrig = ["responsavel_nome_completo", "responsavel_parentesco", "responsavel_telefone"]
        falt_resp = [c for c in resp_obrig if not _norm(form.get(c))]
        if falt_resp:
            return jsonify({
                "erro": "Aluno menor de idade: campos do responsável são obrigatórios",
                "faltando": falt_resp
            }), 400

        responsavel_obj = Responsavel(
            # ajuste estes campos de acordo com seu model Responsavel real:
            nome=_norm(form.get("responsavel_nome_completo")),
            sobrenome="",  # se seu model exige sobrenome separado, você pode fazer split aqui
            parentesco=_none_if_empty(form.get("responsavel_parentesco")),
            telefone=only_digits(form.get("responsavel_telefone")) or None,
            cidade=_none_if_empty(form.get("responsavel_municipio")),
            bairro=_none_if_empty(form.get("responsavel_bairro")),
            rua=_none_if_empty(form.get("responsavel_endereco")),
        )

        resp_cep = only_digits(form.get("responsavel_cep"))
        if resp_cep and len(resp_cep) != 8:
            return jsonify({"erro": "CEP do responsável inválido (8 dígitos)"}), 400

    try:
        # duplicidade CPF (se sua tabela aluno tiver cpf)
        if hasattr(Aluno, "cpf"):
            if Aluno.query.filter_by(cpf=cpf).first():
                return jsonify({"erro": "Já existe aluno cadastrado com este CPF"}), 409

        # foto
        foto_filename = None
        if "foto" in request.files and request.files["foto"].filename:
            foto_filename = _save_photo(request.files["foto"], form.get("nome_completo"))

        if responsavel_obj:
            db.session.add(responsavel_obj)
            db.session.flush()  # garante id

        # ========= CRIA ALUNO (só seta colunas que existem no seu model) =========
        aluno = Aluno(
            # seu banco/model atual é o "novo" (nome/sobrenome/cidade/rua...)
            # mas seu FORM é o "antigo" (nome_completo/endereco/municipio).
            # então fazemos o mapeamento abaixo.

            nome=_norm(form.get("nome_completo")),   # cai tudo aqui
            sobrenome="",                            # mantém vazio para não quebrar
            matricula=_norm(form.get("matricula")),

            cidade=_norm(form.get("municipio")),     # municipio -> cidade
            bairro=_norm(form.get("bairro")),
            rua=_norm(form.get("endereco")),         # endereco -> rua

            idade=idade,
            empregado="nao",                         # seu form atual não manda "empregado"

            telefone=only_digits(form.get("telefone")) or None,
            data_nascimento=data_nasc,

            # estes 3 NÃO estão chegando no form atual -> salve default ou permita NULL no banco/model
            linha_atendimento=_norm(form.get("linha_atendimento") or "CAI"),
            escola_integrada=_norm(form.get("escola_integrada") or "Nenhuma"),

            curso=_norm(form.get("curso")),
            turma=_norm(form.get("turma")),

            outras_informacoes=_none_if_empty(form.get("parceria_novo_ensino_medio")),
            pessoa_com_deficiencia=False,

            responsavel_id=(responsavel_obj.id if responsavel_obj else None),
        )

        # foto só se existir no model
        if hasattr(aluno, "foto"):
            aluno.foto = foto_filename

        db.session.add(aluno)
        db.session.commit()
        return jsonify({"mensagem": "Aluno cadastrado com sucesso!", "id": aluno.id}), 201

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao cadastrar aluno")
        return jsonify({"erro": "Erro ao cadastrar aluno"}), 500
