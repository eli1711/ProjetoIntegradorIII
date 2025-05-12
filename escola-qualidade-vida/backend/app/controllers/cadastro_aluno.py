from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno
from app import db
import os

cadastro_bp = Blueprint('cadastro', __name__, url_prefix='/cadastro')

@cadastro_bp.route('/aluno', methods=['POST'])
def cadastrar_aluno():
    data = request.form.to_dict()  # Dados enviados via form-data

    try:
        # Verificação dos dados obrigatórios
        if not all([data.get('nome'), data.get('sobrenome'), data.get('cidade'), data.get('bairro'), data.get('rua'), data.get('idade')]):
            return jsonify({'erro': 'Todos os campos obrigatórios devem ser preenchidos'}), 400

        # Verificar se o aluno é menor de idade e se é necessário cadastrar um responsável
        idade = int(data.get('idade'))
        if idade < 18:
            if not all([data.get('nomeResponsavel'), data.get('sobrenomeResponsavel'), data.get('parentescoResponsavel')]):
                return jsonify({'erro': 'É necessário preencher os dados do responsável para alunos menores de 18 anos.'}), 400

        # Verificar se o aluno é empregado e se é necessário cadastrar a empresa
        empregado = data.get('empregado', 'nao')
        if empregado == 'sim' and not data.get('empresa'):
            return jsonify({'erro': 'Se o aluno for empregado, é necessário preencher o campo da empresa.'}), 400

        # Criação do objeto Aluno
        aluno = Aluno(
            nome=data['nome'],
            sobrenome=data['sobrenome'],
            cidade=data['cidade'],
            bairro=data['bairro'],
            rua=data['rua'],
            idade=idade,
            empregado=empregado,
            empresa=data.get('empresa'),
            comorbidade=data.get('comorbidade'),
            nome_responsavel=data.get('nomeResponsavel'),
            sobrenome_responsavel=data.get('sobrenomeResponsavel'),
            parentesco_responsavel=data.get('parentescoResponsavel'),
            telefone_responsavel=data.get('telefoneResponsavel')
        )

        # Salvar a foto, se fornecida
        if 'foto' in request.files:
            foto = request.files['foto']
            foto_path = os.path.join('uploads', foto.filename)
            foto.save(foto_path)
            aluno.foto = foto_path

        # Salvar no banco de dados
        db.session.add(aluno)
        db.session.commit()

        return jsonify({'mensagem': 'Cadastro realizado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar o aluno', 'detalhes': str(e)}), 500
