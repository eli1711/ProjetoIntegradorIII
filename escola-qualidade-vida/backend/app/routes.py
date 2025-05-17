from flask import request, redirect, url_for, jsonify
from app import db
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.empresa import Empresa
import os

@app.route('/cadastrar-aluno', methods=['POST'])
def cadastrar_aluno():
    try:
        # Captura os dados do formulário
        data = request.form.to_dict()
        
        # Validação dos dados obrigatórios
        if not all([data.get('nome'), data.get('sobrenome'), data.get('cidade'), data.get('bairro'), data.get('rua'), data.get('idade')]):
            return jsonify({'erro': 'Todos os campos obrigatórios devem ser preenchidos'}), 400

        # Verificação do responsável se o aluno for menor de idade
        idade = int(data['idade'])
        responsavel_id = None
        if idade < 18:
            if not all([data.get('nome_responsavel'), data.get('sobrenome_responsavel'), data.get('telefone_responsavel'), data.get('endereco_responsavel')]):
                return jsonify({'erro': 'Dados do responsável são obrigatórios para alunos menores de 18 anos.'}), 400
            responsavel = Responsavel(
                nome=data['nome_responsavel'],
                sobrenome=data['sobrenome_responsavel'],
                telefone=data['telefone_responsavel'],
                endereco=data['endereco_responsavel']
            )
            db.session.add(responsavel)
            db.session.commit()
            responsavel_id = responsavel.id

        # Verificação da empresa se o aluno for empregado
        empresa_id = None
        if data.get('empregado') == 'sim':
            if not all([data.get('nome_empresa'), data.get('endereco_empresa'), data.get('telefone_empresa')]):
                return jsonify({'erro': 'Dados da empresa são obrigatórios para alunos empregados.'}), 400
            empresa = Empresa(
                nome=data['nome_empresa'],
                endereco=data['endereco_empresa'],
                telefone=data['telefone_empresa']
            )
            db.session.add(empresa)
            db.session.commit()
            empresa_id = empresa.id

        # Salvando a foto, se fornecida
        foto_filename = None
        if 'foto' in request.files:
            foto = request.files['foto']
            foto_filename = foto.filename
            foto_path = os.path.join('uploads', foto_filename)
            foto.save(foto_path)

        # Criando o aluno
        novo_aluno = Aluno(
            nome=data['nome'],
            sobrenome=data['sobrenome'],
            cidade=data['cidade'],
            bairro=data['bairro'],
            rua=data['rua'],
            idade=idade,
            empregado=data['empregado'],
            coma_com_quem=data.get('coma_com_quem'),
            sobre_aluno=data.get('sobre_aluno'),
            foto=foto_filename,
            responsavel_id=responsavel_id,
            empresa_id=empresa_id
        )

        # Adicionando o aluno ao banco de dados
        db.session.add(novo_aluno)
        db.session.commit()

        return jsonify({'mensagem': 'Cadastro realizado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar aluno', 'detalhes': str(e)}), 500
