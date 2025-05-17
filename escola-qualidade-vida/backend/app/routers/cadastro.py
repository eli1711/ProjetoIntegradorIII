from flask import Blueprint, request, jsonify
from app import db
from app.models.aluno import Aluno
import os

# Criação do Blueprint
cadastro_bp = Blueprint('cadastro', __name__)

@cadastro_bp.route('/cadastrar-aluno', methods=['POST'])
def cadastrar_aluno():
    if request.method == 'POST':
        # Captura os dados do formulário
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        cidade = request.form['cidade']
        bairro = request.form['bairro']
        rua = request.form['rua']
        idade = request.form['idade']
        empregado = request.form['empregado']
        mora_com_quem = request.form['mora_com_quem']
        sobre_aluno = request.form['sobre_aluno']
        
        # Processando o upload da foto
        foto = request.files['foto']
        foto_filename = None
        if foto:
            foto_filename = foto.filename
            if not os.path.exists('./uploads'):
                os.makedirs('./uploads')  # Cria o diretório de uploads se necessário
            foto.save(f'./uploads/{foto_filename}')  # Salva a foto no diretório de uploads

        # Criando o objeto aluno
        novo_aluno = Aluno(
            nome=nome, sobrenome=sobrenome, cidade=cidade, bairro=bairro, rua=rua, 
            idade=idade, empregado=empregado, coma_com_quem=mora_com_quem, sobre_aluno=sobre_aluno, foto=foto_filename
        )

        # Adicionando o aluno ao banco de dados
        db.session.add(novo_aluno)
        db.session.commit()

        # Retornando a resposta JSON de sucesso
        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201
