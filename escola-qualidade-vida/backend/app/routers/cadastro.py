import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app import db
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.empresa import Empresa


# Função utilitária: converte valores do HTML em booleanos compatíveis
def str_to_bool(value):
    return str(value).lower() in ["true", "1", "on", "t", "yes", "y", "sim"]


# Função para salvar a foto do aluno
def salvar_foto(foto_file, aluno_nome, destino="/backend/app/uploads"):
    caminho_absoluto = os.path.join(os.path.abspath(os.path.dirname(__file__)), destino)

    if not os.path.exists(caminho_absoluto):
        os.makedirs(caminho_absoluto)

    ext = os.path.splitext(foto_file.filename)[1].lower()
    aluno_nome_securizado = secure_filename(aluno_nome.lower())
    filename = f"{aluno_nome_securizado}{ext}"
    caminho = os.path.join(caminho_absoluto, filename)

    contador = 1
    while os.path.exists(caminho):
        filename = f"{aluno_nome_securizado}_{contador}{ext}"
        caminho = os.path.join(caminho_absoluto, filename)
        contador += 1

    foto_file.save(caminho)
    return filename


# Blueprint
cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")


@cadastro_bp.route("/alunos", methods=["POST"])
def cadastrar_aluno():
    data = request.form.to_dict()

    try:
        obrigatorios = [
            "nome", "sobrenome", "matricula", "cidade", "bairro", "rua",
            "idade", "curso", "linha_atendimento", "escola_integrada"
        ]

        if not all(data.get(campo) for campo in obrigatorios):
            return jsonify({"erro": "Campos obrigatórios não preenchidos"}), 400

        idade = int(data.get("idade"))
        curso_id = int(data.get("curso"))

        # Boolean compatível
        pessoa_com_deficiencia = str_to_bool(data.get("pessoa_com_deficiencia"))
        deficiencia_descricao = (data.get("deficiencia_descricao") or "").strip()
        empregado = data.get("empregado", "nao")

        # Montagem de observações e deficiência
        outras_informacoes = (data.get("outras_informacoes") or "").strip()
        if pessoa_com_deficiencia and deficiencia_descricao:
            bloco_def = f"Deficiência: {deficiencia_descricao}"
            outras_informacoes = (
                f"{bloco_def}\n{outras_informacoes}".strip()
                if outras_informacoes
                else bloco_def
            )

        # Empresa contratante (se for empregado)
        empresa_contratante = None
        if empregado == "sim":
            empresa_contratante = data.get("empresa")
            if not empresa_contratante:
                return jsonify({"erro": "Nome da empresa é obrigatório."}), 400

        # Responsável (se menor)
        responsavel_id = None
        if idade < 18:
            if not all(
                data.get(f)
                for f in ["nomeResponsavel", "sobrenomeResponsavel", "parentescoResponsavel"]
            ):
                return jsonify(
                    {"erro": "Dados do responsável são obrigatórios para menores de idade."}
                ), 400
            responsavel = Responsavel(
                nome=data["nomeResponsavel"],
                sobrenome=data["sobrenomeResponsavel"],
                parentesco=data["parentescoResponsavel"],
                telefone=data.get("telefone_responsavel"),
                cidade=data.get("cidade_responsavel"),
                bairro=data.get("bairro_responsavel"),
                rua=data.get("rua_responsavel"),
            )
            db.session.add(responsavel)
            db.session.flush()
            responsavel_id = responsavel.id

        # Empresa (se empregado)
        empresa_id = None
        if empregado == "sim":
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

        # Foto (upload)
        foto_filename = None
        if "foto" in request.files and request.files["foto"].filename:
            foto_filename = salvar_foto(request.files["foto"], data["nome"])

        # Criação do objeto Aluno
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
            foto=foto_filename,
            data_nascimento=data.get("data_nascimento"),
            linha_atendimento=data["linha_atendimento"],
            escola_integrada=data["escola_integrada"],
            pessoa_com_deficiencia=pessoa_com_deficiencia,
            outras_informacoes=outras_informacoes,
            curso_id=curso_id,
            curso=data.get("curso_nome"),  # se quiser salvar também o nome literal
            turma=data.get("turma"),
            data_inicio_curso=data.get("data_inicio_curso"),
            empresa_contratante=empresa_contratante,
            responsavel_id=responsavel_id,
            empresa_id=empresa_id,
        )

        db.session.add(aluno)
        db.session.commit()

        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"erro": "Erro ao cadastrar aluno", "detalhes": str(e)}), 500
