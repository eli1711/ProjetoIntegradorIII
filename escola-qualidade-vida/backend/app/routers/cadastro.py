import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models.aluno import Aluno
from app.models.empresa import Empresa
from app.models.responsavel import Responsavel
from werkzeug.utils import secure_filename
import os

cadastro_bp = Blueprint('cadastro', __name__, url_prefix='/cadastro')

# Configurar logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Função auxiliar para salvar fotos evitando conflitos de nome
def salvar_foto(foto_file, destino='/app/uploads'):
    if not os.path.exists(destino):
        os.makedirs(destino)

    filename = secure_filename(foto_file.filename)
    caminho = os.path.join(destino, filename)

    contador = 1
    nome, ext = os.path.splitext(filename)
    while os.path.exists(caminho):
        filename = f"{nome}_{contador}{ext}"
        caminho = os.path.join(destino, filename)
        contador += 1

    logger.info(f"Salvando foto em: {caminho}")
    foto_file.save(caminho)
    return filename

@cadastro_bp.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    data = request.form.to_dict()

    try:
        # Validação campos obrigatórios
        obrigatorios = ['nome', 'sobrenome', 'cidade', 'bairro', 'rua', 'idade', 'curso']
        if not all(data.get(campo) for campo in obrigatorios):
            return jsonify({'erro': 'Campos obrigatórios não preenchidos'}), 400

        idade = int(data.get('idade'))
        curso_id = int(data.get('curso'))  # Novo campo curso_id
        if idade < 18:
            resp_fields = ['nomeResponsavel', 'sobrenomeResponsavel', 'parentescoResponsavel']
            if not all(data.get(f) for f in resp_fields):
                return jsonify({'erro': 'Dados do responsável são obrigatórios para menores de 18 anos.'}), 400

        empregado = data.get('empregado', 'nao')
        if empregado == 'sim' and not data.get('empresa'):
            return jsonify({'erro': 'Campo empresa é obrigatório se aluno for empregado.'}), 400

        aluno = Aluno(
            nome=data['nome'],
            sobrenome=data['sobrenome'],
            cidade=data['cidade'],
            bairro=data['bairro'],
            rua=data['rua'],
            idade=idade,
            empregado=empregado,
            mora_com_quem=data.get('mora_com_quem'),
            sobre_aluno=data.get('sobre_aluno'),
            curso_id=curso_id,  # Adicionando curso_id
            responsavel_id=None,
            empresa_id=None
        )

        if idade < 18:
            responsavel = Responsavel(
                nome=data['nomeResponsavel'],
                sobrenome=data['sobrenomeResponsavel'],
                parentesco=data.get('parentescoResponsavel'),
                telefone=data.get('telefone_responsavel'),
                cidade=data.get('cidade_responsavel'),
                bairro=data.get('bairro_responsavel'),
                rua=data.get('rua_responsavel')
            )
            db.session.add(responsavel)
            db.session.flush()
            aluno.responsavel_id = responsavel.id

        if empregado == 'sim':
            empresa = Empresa(
                nome=data['empresa'],
                endereco=data.get('endereco_empresa'),
                telefone=data.get('telefone_empresa'),
                cidade=data.get('cidade_empresa'),
                bairro=data.get('bairro_empresa'),
                rua=data.get('rua_empresa')
            )
            db.session.add(empresa)
            db.session.flush()
            aluno.empresa_id = empresa.id

        if 'foto' in request.files:
            aluno.foto = salvar_foto(request.files['foto'])

        db.session.add(aluno)
        db.session.commit()

        return jsonify({'mensagem': 'Cadastro realizado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'erro': 'Erro ao cadastrar aluno', 'detalhes': str(e)}), 500
