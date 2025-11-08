# app/routers/cadastro.py
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.empresa import Empresa
from app.models.turma import Turma

def str_to_bool(value):
    return str(value).lower() in ["true", "1", "on", "t", "yes", "y", "sim"]

def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        return None

def salvar_foto(foto_file, aluno_nome):
    """Salva a foto **exatamente** na pasta configurada em UPLOAD_FOLDER."""
    upload_dir = current_app.config["UPLOAD_FOLDER"]  # << chave da correção
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(foto_file.filename)[1].lower()
    base = secure_filename((aluno_nome or "aluno").lower())
    filename = f"{base}{ext}"
    dest = os.path.join(upload_dir, filename)

    i = 1
    while os.path.exists(dest):
        filename = f"{base}_{i}{ext}"
        dest = os.path.join(upload_dir, filename)
        i += 1

    foto_file.save(dest)
    current_app.logger.info(f"🖼️ Foto salva em: {dest}")
    return filename  # importante: salve só o nome, a rota /uploads/<nome> serve o arquivo

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

@cadastro_bp.route("/alunos", methods=["POST"])
def cadastrar_aluno():
    data = request.form.to_dict()
    try:
        obrigatorios = ["nome","sobrenome","matricula","cidade","bairro","rua",
                        "idade","curso","linha_atendimento","escola_integrada"]
        if not all(data.get(c) for c in obrigatorios):
            return jsonify({"erro": "Campos obrigatórios não preenchidos"}), 400

        idade = int(data["idade"])
        curso_id = int(data["curso"])

        turma_id_raw = request.form.get("turma_id")
        if not turma_id_raw:
            return jsonify({"erro": "Selecione uma turma válida."}), 400
        turma_id = int(turma_id_raw)
        turma_obj = Turma.query.get(turma_id)
        if not turma_obj:
            return jsonify({"erro": "Turma não encontrada."}), 400
        if turma_obj.curso_id != curso_id:
            return jsonify({"erro": "A turma selecionada não pertence ao curso escolhido."}), 400

        pessoa_com_deficiencia = str_to_bool(data.get("pessoa_com_deficiencia"))
        deficiencia_descricao = (data.get("deficiencia_descricao") or "").strip()
        empregado = data.get("empregado", "nao")

        outras_informacoes = (data.get("outras_informacoes") or "").strip()
        if pessoa_com_deficiencia and deficiencia_descricao:
            bloco = f"Deficiência: {deficiencia_descricao}"
            outras_informacoes = f"{bloco}\n{outras_informacoes}".strip() if outras_informacoes else bloco

        empresa_contratante = None
        empresa_id = None
        if empregado == "sim":
            empresa_contratante = data.get("empresa")
            if not empresa_contratante:
                return jsonify({"erro": "Nome da empresa é obrigatório."}), 400
            empresa = Empresa(
                nome=data["empresa"],
                endereco=data.get("endereco_empresa"),
                telefone=data.get("telefone_empresa"),
                cidade=data.get("cidade_empresa"),
                bairro=data.get("bairro_empresa"),
                rua=data.get("rua_empresa"),
            )
            db.session.add(empresa)
            db.session.flush()
            empresa_id = empresa.id

        responsavel_id = None
        if idade < 18:
            req_resp = ["nomeResponsavel","sobrenomeResponsavel","parentescoResponsavel"]
            if not all(data.get(f) for f in req_resp):
                return jsonify({"erro": "Dados do responsável são obrigatórios para menores de idade."}), 400
            resp = Responsavel(
                nome=data["nomeResponsavel"],
                sobrenome=data["sobrenomeResponsavel"],
                parentesco=data["parentescoResponsavel"],
                telefone=data.get("telefone_responsavel"),
                cidade=data.get("cidade_responsavel"),
                bairro=data.get("bairro_responsavel"),
                rua=data.get("rua_responsavel"),
            )
            db.session.add(resp)
            db.session.flush()
            responsavel_id = resp.id

        foto_filename = None
        if "foto" in request.files and request.files["foto"].filename:
            foto_filename = salvar_foto(request.files["foto"], data.get("nome"))

        data_nascimento = _parse_date(data.get("data_nascimento"))
        data_inicio_curso = _parse_date(data.get("data_inicio_curso"))

        aluno = Aluno(
            nome=data["nome"],
            sobrenome=data["sobrenome"],
            matricula=data["matricula"],
            cidade=data["cidade"],
            bairro=data["bairro"],
            rua=data["rua"],
            idade=idade,
            empregado=empregado,
            mora_com_quem=data.get("mora_com_quem"),
            sobre_aluno=data.get("sobre_aluno"),
            foto=foto_filename,  # << guarda só o nome
            data_nascimento=data_nascimento,
            linha_atendimento=data["linha_atendimento"],
            escola_integrada=data["escola_integrada"],
            pessoa_com_deficiencia=pessoa_com_deficiencia,
            outras_informacoes=outras_informacoes,
            curso_id=curso_id,
            curso=data.get("curso_nome"),
            turma=data.get("turma"),
            data_inicio_curso=data_inicio_curso,
            empresa_contratante=empresa_contratante,
            responsavel_id=responsavel_id,
            empresa_id=empresa_id,
            turma_id=turma_id,
        )

        db.session.add(aluno)
        db.session.commit()
        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao cadastrar aluno", "detalhes": str(e)}), 500
