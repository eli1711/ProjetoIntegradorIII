from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.aluno import Aluno
from app import db
import os

cadastro_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

@cadastro_bp.route('/cadastrar', methods=['POST'])
@jwt_required()
def cadastrar_aluno():
    """Registra um novo aluno no sistema."""
    try:
        data = request.form.to_dict()  # dados enviados via form-data (possível foto)
        # Campos obrigatórios
        nome = data.get('nome')
        sobrenome = data.get('sobrenome')
        cidade = data.get('cidade')
        bairro = data.get('bairro')
        rua = data.get('rua')
        idade = data.get('idade')
        if not all([nome, sobrenome, cidade, bairro, rua, idade]):
            return jsonify({'erro': 'Todos os campos obrigatórios devem ser preenchidos'}), 400

        # Campos opcionais ou de preenchimento condicional
        idade = int(idade)
        empregado = data.get('empregado', 'nao')
        empresa = data.get('empresa')
        comorbidade = data.get('comorbidade')
        nome_responsavel = data.get('nomeResponsavel')
        sobrenome_responsavel = data.get('sobrenomeResponsavel')
        parentesco = data.get('parentescoResponsavel')
        telefone_responsavel = data.get('telefoneResponsavel')

        # Cria instância de Aluno
        aluno = Aluno(
            nome=nome,
            sobrenome=sobrenome,
            cidade=cidade,
            bairro=bairro,
            rua=rua,
            idade=idade,
            empregado=empregado,
            empresa=empresa,
            comorbidade=comorbidade,
            nome_responsavel=nome_responsavel,
            sobrenome_responsavel=sobrenome_responsavel,
            parentesco_responsavel=parentesco,
            telefone_responsavel=telefone_responsavel
        )

        # Trata upload de foto, se enviado
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename:
                os.makedirs('uploads', exist_ok=True)  # garante diretório de uploads
                upload_path = os.path.join('uploads', foto.filename)
                foto.save(upload_path)
                aluno.foto = upload_path

        # Salva no banco de dados
        db.session.add(aluno)
        db.session.commit()
        return jsonify({'mensagem': 'Aluno cadastrado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar o aluno', 'detalhes': str(e)}), 500

@cadastro_bp.route('/consultar', methods=['GET'])
@jwt_required()
def consultar_aluno():
    """Consulta um aluno por ID ou nome (query params ?id= ou ?nome=)."""
    aluno_id = request.args.get('id')
    nome = request.args.get('nome')
    aluno = None
    if aluno_id:
        aluno = Aluno.query.get(int(aluno_id))
    elif nome:
        aluno = Aluno.query.filter_by(nome=nome).first()

    if not aluno:
        return jsonify({'erro': 'Aluno não encontrado'}), 404

    # Prepara os dados do aluno para retorno
    aluno_data = {
        'id': aluno.id,
        'nome': aluno.nome,
        'sobrenome': aluno.sobrenome,
        'cidade': aluno.cidade,
        'bairro': aluno.bairro,
        'rua': aluno.rua,
        'idade': aluno.idade,
        'empregado': aluno.empregado,
        'empresa': aluno.empresa,
        'comorbidade': aluno.comorbidade,
        'nome_responsavel': aluno.nome_responsavel,
        'sobrenome_responsavel': aluno.sobrenome_responsavel,
        'parentesco_responsavel': aluno.parentesco_responsavel,
        'telefone_responsavel': aluno.telefone_responsavel,
        'foto': aluno.foto
    }
    return jsonify(aluno_data), 200
