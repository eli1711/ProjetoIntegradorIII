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

    # ========= CAMPOS OBRIGATÓRIOS =========
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

    # ========= VERIFICA SE CPF JÁ EXISTE =========
    aluno_existente = Aluno.query.filter_by(cpf=cpf).first()
    if aluno_existente:
        return jsonify({"erro": "Já existe aluno cadastrado com este CPF"}), 409

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
            nome=_norm(form.get("responsavel_nome_completo")),
            sobrenome="",
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
        # foto
        foto_filename = None
        if "foto" in request.files and request.files["foto"].filename:
            foto_filename = _save_photo(request.files["foto"], form.get("nome_completo"))

        if responsavel_obj:
            db.session.add(responsavel_obj)
            db.session.flush()  # garante id

        # ========= SEPARA NOME COMPLETO EM NOME E SOBRENOME =========
        nome_completo = _norm(form.get("nome_completo"))
        nome = ""
        sobrenome = ""
        
        if nome_completo:
            # Divide o nome completo em partes
            partes = nome_completo.split(' ', 1)
            nome = partes[0] if partes else ""
            sobrenome = partes[1] if len(partes) > 1 else ""

        # ========= CRIA ALUNO COM CPF OBRIGATÓRIO =========
        aluno = Aluno(
            # ✅ CPF OBRIGATÓRIO (não pode ser NULL)
            cpf=cpf,
            
            # Nome completo e dividido
            nome_completo=nome_completo,
            nome=nome,
            sobrenome=sobrenome,
            
            
            nome_social=_none_if_empty(form.get("nome_social")),
            
            
            matricula=_norm(form.get("matricula")),
            cidade=_norm(form.get("municipio")),
            bairro=_norm(form.get("bairro")),
            rua=_norm(form.get("endereco")),
            
            idade=idade,
            empregado="nao",  # default
            
            telefone=only_digits(form.get("telefone")) or None,
            data_nascimento=data_nasc,
            
            linha_atendimento=_norm(form.get("linha_atendimento") or "CAI"),
            escola_integrada=_norm(form.get("escola_integrada") or "Nenhuma"),
            
            curso=_norm(form.get("curso")),
            turma=_norm(form.get("turma")),
            
            outras_informacoes=_none_if_empty(form.get("parceria_novo_ensino_medio")),
            pessoa_com_deficiencia=pne,
            
            responsavel_id=(responsavel_obj.id if responsavel_obj else None),
        )

        # Normaliza os dados
        aluno.normalize()
        
        # foto
        if hasattr(aluno, "foto"):
            aluno.foto = foto_filename

        db.session.add(aluno)
        db.session.commit()
        
        return jsonify({
            "mensagem": "Aluno cadastrado com sucesso!", 
            "id": aluno.id,
            "cpf": aluno.cpf
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Erro ao cadastrar aluno: {str(e)}")
        return jsonify({"erro": f"Erro ao cadastrar aluno: {str(e)}"}), 500