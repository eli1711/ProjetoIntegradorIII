from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno
from app import db
import os

# Define o Blueprint para as rotas de cadastro
cadastro_bp = Blueprint('cadastro', __name__, url_prefix='/cadastro')

@cadastro_bp.route('/aluno', methods=['POST'])
def cadastrar_aluno():
    data = request.get_json()

    try:
        # Verificação dos dados obrigatórios
        if not all([data.get('nome'), data.get('sobrenome'), data.get('cidade'), data.get('bairro'), data.get('rua'), data.get('idade')]):
            return jsonify({'erro': 'Todos os campos obrigatórios devem ser preenchidos'}), 400

        # Criação do objeto Aluno
        aluno = Aluno(
            nome=data['nome'],
            sobrenome=data['sobrenome'],
            cidade=data['cidade'],
            bairro=data['bairro'],
            rua=data['rua'],
            idade=data['idade'],
            empregado=data.get('empregado', 'nao'),
            coma_com_quem=data.get('coma_com_quem'),
            comorbidade=data.get('comorbidade')
        )

        # Salvar a foto, se fornecida
        if 'foto' in request.files:
            foto = request.files['foto']
            foto_path = os.path.join('uploads', foto.filename)  # Defina o diretório de uploads conforme necessário
            foto.save(foto_path)
            aluno.foto = foto_path  # Armazena o caminho da foto no banco de dados

        # Salvar no banco de dados
        db.session.add(aluno)
        db.session.commit()

        return jsonify({'mensagem': 'Cadastro realizado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar o aluno', 'detalhes': str(e)}), 500
