import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app import db
from app.models.aluno import Aluno
from app.services.upload_service import salvar_foto
from app.models.responsavel import Responsavel
from app.models.empresa import Empresa

# Função para salvar a foto com o nome do aluno
def salvar_foto(foto_file, aluno_nome, destino='/backend/app/uploads'):
    caminho_absoluto = os.path.join(os.path.abspath(os.path.dirname(__file__)), destino)

    # Verificar se o diretório de uploads existe, senão, criar
    if not os.path.exists(caminho_absoluto):
        os.makedirs(caminho_absoluto)

    # Obter a extensão da imagem
    ext = os.path.splitext(foto_file.filename)[1].lower()

    # Criar o nome do arquivo com o nome do aluno
    aluno_nome_securizado = secure_filename(aluno_nome.lower())  # Convertendo o nome para minúsculas
    filename = f"{aluno_nome_securizado}{ext}"

    caminho = os.path.join(caminho_absoluto, filename)

    # Verificar se já existe um arquivo com esse nome e adicionar um contador caso exista
    contador = 1
    while os.path.exists(caminho):
        filename = f"{aluno_nome_securizado}_{contador}{ext}"
        caminho = os.path.join(caminho_absoluto, filename)
        contador += 1

    # Salvar o arquivo
    foto_file.save(caminho)
    return filename

# Rota de Cadastro do Aluno
cadastro_bp = Blueprint('cadastro', __name__, url_prefix='/cadastro')

@cadastro_bp.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    data = request.form.to_dict()

    try:
        obrigatorios = ['nome', 'sobrenome', 'cidade', 'bairro', 'rua', 'idade', 'curso']
        if not all(data.get(campo) for campo in obrigatorios):
            return jsonify({'erro': 'Campos obrigatórios não preenchidos'}), 400

        idade = int(data.get('idade'))
        curso_id = int(data.get('curso')) 

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
            curso_id=curso_id,
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

        # Salvar a foto
        if 'foto' in request.files:
            aluno_nome = data['nome']  # Usando o nome do aluno para renomear a foto
            aluno.foto = salvar_foto(request.files['foto'], aluno_nome, destino='/backend/app/uploads')

        db.session.add(aluno)
        db.session.commit()

        return jsonify({'mensagem': 'Cadastro realizado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'erro': 'Erro ao cadastrar aluno', 'detalhes': str(e)}), 500
