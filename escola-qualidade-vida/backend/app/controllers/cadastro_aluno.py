# app/controllers/cadastro_aluno.py
from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno, db

cadastro_bp = Blueprint('cadastro', __name__, url_prefix='/cadastro')

@cadastro_bp.route('/aluno', methods=['POST'])
def cadastrar_aluno():
    # Coleta de dados enviados via JSON
    data = request.get_json()

    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    cidade = data.get('cidade')
    bairro = data.get('bairro')
    rua = data.get('rua')
    idade = data.get('idade')

    # Verificando se todos os campos necessários estão presentes
    if not nome or not sobrenome or not cidade or not bairro or not rua or not idade:
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    # Criando o novo aluno
    novo_aluno = Aluno(
        nome=nome,
        sobrenome=sobrenome,
        cidade=cidade,
        bairro=bairro,
        rua=rua,
        idade=idade
    )

    try:
        db.session.add(novo_aluno)
        db.session.commit()
        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao cadastrar aluno: {str(e)}"}), 500
