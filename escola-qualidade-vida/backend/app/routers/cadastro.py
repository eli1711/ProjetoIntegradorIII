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
    upload_dir = current_app.config["UPLOAD_FOLDER"]
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
    return filename

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")

@cadastro_bp.route("/alunos", methods=["POST"])
def cadastrar_aluno():
    # ✅ NÃO converte para dict; usa request.form diretamente
    form = request.form

    # Logs de diagnóstico
    try:
        current_app.logger.info(f"📝 form keys: {list(form.keys())}")
        current_app.logger.info(f"📞 telefone (bruto): {form.get('telefone')}")
    except Exception:
        pass

    try:
        # Campos obrigatórios
        obrigatorios = [
            "nome", "sobrenome", "matricula", "cidade", "bairro", "rua",
            "idade", "curso", "linha_atendimento", "escola_integrada"
        ]
        faltando = [c for c in obrigatorios if not form.get(c)]
        if faltando:
            return jsonify({"erro": "Campos obrigatórios não preenchidos", "faltando": faltando}), 400

        # Conversões
        idade = int(form.get("idade"))
        curso_id = int(form.get("curso"))

        # Telefone (garante persistência)
        telefone = (form.get("telefone") or "").strip()
        if telefone == "":
            telefone = None  # salva NULL em vez de string vazia

        # Turma (FK)
        turma_id_raw = form.get("turma_id")
        if not turma_id_raw:
            return jsonify({"erro": "Selecione uma turma válida."}), 400
        turma_id = int(turma_id_raw)
        turma_obj = Turma.query.get(turma_id)
        if not turma_obj:
            return jsonify({"erro": "Turma não encontrada."}), 400
        if turma_obj.curso_id != curso_id:
            return jsonify({"erro": "A turma selecionada não pertence ao curso escolhido."}), 400

        # Flags e textos
        pessoa_com_deficiencia = str_to_bool(form.get("pessoa_com_deficiencia"))
        deficiencia_descricao = (form.get("deficiencia_descricao") or "").strip()
        empregado = (form.get("empregado") or "nao").strip()

        outras_informacoes = (form.get("outras_informacoes") or "").strip()
        if pessoa_com_deficiencia and deficiencia_descricao:
            bloco = f"Deficiência: {deficiencia_descricao}"
            outras_informacoes = f"{bloco}\n{outras_informacoes}".strip() if outras_informacoes else bloco

        # Empresa (se empregado)
        empresa_contratante = None
        empresa_id = None
        if empregado == "sim":
            empresa_contratante = form.get("empresa")
            if not empresa_contratante:
                return jsonify({"erro": "Nome da empresa é obrigatório."}), 400
            empresa = Empresa(
                nome=form.get("empresa"),
                endereco=form.get("endereco_empresa"),
                telefone=form.get("telefone_empresa"),
                cidade=form.get("cidade_empresa"),
                bairro=form.get("bairro_empresa"),
                rua=form.get("rua_empresa"),
            )
            db.session.add(empresa)
            db.session.flush()
            empresa_id = empresa.id

        # Responsável (se menor)
        responsavel_id = None
        if idade < 18:
            req_resp = ["nomeResponsavel", "sobrenomeResponsavel", "parentescoResponsavel"]
            if not all(form.get(f) for f in req_resp):
                return jsonify({"erro": "Dados do responsável são obrigatórios para menores de idade."}), 400
            resp = Responsavel(
                nome=form.get("nomeResponsavel"),
                sobrenome=form.get("sobrenomeResponsavel"),
                parentesco=form.get("parentescoResponsavel"),
                telefone=form.get("telefone_responsavel"),
                cidade=form.get("cidade_responsavel"),
                bairro=form.get("bairro_responsavel"),
                rua=form.get("rua_responsavel"),
            )
            db.session.add(resp)
            db.session.flush()
            responsavel_id = resp.id

        # Foto (opcional)
        foto_filename = None
        if "foto" in request.files and request.files["foto"].filename:
            foto_filename = salvar_foto(request.files["foto"], form.get("nome"))

        # Datas
        data_nascimento = _parse_date(form.get("data_nascimento"))
        data_inicio_curso = _parse_date(form.get("data_inicio_curso"))

        # Cria o aluno
        aluno = Aluno(
            nome=form.get("nome"),
            sobrenome=form.get("sobrenome"),
            matricula=form.get("matricula"),
            cidade=form.get("cidade"),
            bairro=form.get("bairro"),
            rua=form.get("rua"),
            idade=idade,
            empregado=empregado,
            mora_com_quem=form.get("mora_com_quem"),
            sobre_aluno=form.get("sobre_aluno"),
            foto=foto_filename,
            telefone=telefone,  # ✅ agora vai pro banco
            data_nascimento=data_nascimento,
            linha_atendimento=form.get("linha_atendimento"),
            escola_integrada=form.get("escola_integrada"),
            pessoa_com_deficiencia=pessoa_com_deficiencia,
            outras_informacoes=outras_informacoes,
            curso_id=curso_id,
            curso=form.get("curso_nome"),
            turma=form.get("turma"),  # rótulo textual (compat)
            data_inicio_curso=data_inicio_curso,
            empresa_contratante=empresa_contratante,
            responsavel_id=responsavel_id,
            empresa_id=empresa_id,
            turma_id=turma_id,
        )

        db.session.add(aluno)
        db.session.commit()

        current_app.logger.info(f"✅ Aluno salvo (id={aluno.id}) com telefone={aluno.telefone!r}")
        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro ao cadastrar aluno")
        return jsonify({"erro": "Erro ao cadastrar aluno", "detalhes": str(e)}), 500
