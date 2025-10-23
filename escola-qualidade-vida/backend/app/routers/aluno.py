import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app import db
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.empresa import Empresa


aluno_bp = Blueprint("aluno", __name__, url_prefix="/alunos")

@aluno_bp.route("/", methods=["GET"])
def listar_alunos():
    return jsonify({"mensagem": "Blueprint 'aluno_bp' ativo e funcionando corretamente!"}), 200

def str_to_bool(value):
    return str(value).lower() in ["true", "1", "on", "t", "yes", "y", "sim"]


def parse_date(value):
    """Converte string de data (YYYY-MM-DD) para objeto date."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None
    except ValueError:
        return None


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

        empregado = data.get("empregado", "nao")
        pessoa_com_deficiencia = str_to_bool(data.get("pessoa_com_deficiencia"))
        deficiencia_descricao = (data.get("deficiencia_descricao") or "").strip()
        outras_informacoes = (data.get("outras_informacoes") or "").strip()

        if pessoa_com_deficiencia and deficiencia_descricao:
            bloco_def = f"Deficiência: {deficiencia_descricao}"
            outras_informacoes = (
                f"{bloco_def}\n{outras_informacoes}".strip()
                if outras_informacoes else bloco_def
            )

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
            foto=None,
            telefone=data.get("telefone"),
            data_nascimento=parse_date(data.get("data_nascimento")),
            linha_atendimento=data["linha_atendimento"],
            curso=data.get("curso"),  # 🔧 corrigido (antes curso_nome)
            turma=data.get("turma"),
            data_inicio_curso=parse_date(data.get("data_inicio_curso")),
            empresa_contratante=data.get("empresa_contratante"),
            escola_integrada=data["escola_integrada"],
            pessoa_com_deficiencia=pessoa_com_deficiencia,
            outras_informacoes=outras_informacoes,
            curso_id=curso_id,
        )

        # Responsável (menores de idade)
        if idade < 18:
            responsavel = Responsavel(
                nome=data.get("nomeResponsavel"),
                sobrenome=data.get("sobrenomeResponsavel"),
                parentesco=data.get("parentescoResponsavel"),
                telefone=data.get("telefone_responsavel"),
                cidade=data.get("cidade_responsavel"),
                bairro=data.get("bairro_responsavel"),
                rua=data.get("rua_responsavel"),
            )
            db.session.add(responsavel)
            db.session.flush()
            aluno.responsavel_id = responsavel.id

        # Empresa (se empregado)
        if empregado == "sim":
            empresa = Empresa(
                nome=data.get("empresa"),
                endereco=data.get("endereco_empresa"),
                telefone=data.get("telefone_empresa"),
                cidade=data.get("cidade_empresa"),
                bairro=data.get("bairro_empresa"),
                rua=data.get("rua_empresa"),
            )
            db.session.add(empresa)
            db.session.flush()
            aluno.empresa_id = empresa.id

        # Upload da foto
        if "foto" in request.files and request.files["foto"].filename:
            aluno.foto = salvar_foto(
                request.files["foto"], data["nome"], destino="/backend/app/uploads"
            )

        db.session.add(aluno)
        db.session.commit()

        return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"erro": "Erro ao cadastrar aluno", "detalhes": str(e)}), 500
