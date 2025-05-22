from flask import Blueprint, request, jsonify
from app import db
from app.models.aluno import Aluno
import os

cadastro_bp = Blueprint('cadastro', __name__, url_prefix='/cadastro')

@cadastro_bp.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    data = request.form.to_dict()

    try:
        # Validar campos obrigatórios
        obrigatorios = ['nome', 'sobrenome', 'cidade', 'bairro', 'rua', 'idade']
        if not all(data.get(campo) for campo in obrigatorios):
            return jsonify({'erro': 'Campos obrigatórios não preenchidos'}), 400

        idade = int(data.get('idade'))
        if idade < 18:
            resp_fields = ['nomeResponsavel', 'sobrenomeResponsavel', 'parentescoResponsavel']
            if not all(data.get(f) for f in resp_fields):
                return jsonify({'erro': 'Dados do responsável são obrigatórios para menores de 18 anos.'}), 400

        empregado = data.get('empregado', 'nao')
        if empregado == 'sim' and not data.get('empresa'):
            return jsonify({'erro': 'Campo empresa é obrigatório se aluno for empregado.'}), 400

        # Criar a instância do aluno
        aluno = Aluno(
            nome=data['nome'],
            sobrenome=data['sobrenome'],
            cidade=data['cidade'],
            bairro=data['bairro'],
            rua=data['rua'],
            idade=idade,
            empregado=empregado,  # Empregado vai ser 'sim' ou 'nao' no banco
            mora_com_quem=data.get('mora_com_quem'),
            sobre_aluno=data.get('sobre_aluno'),
            comorbidade=data.get('comorbidade'),  # Use comorbidade
            descricao_comorbidade=data.get('sobre_aluno'),  # Refatorado para usar 'sobre_aluno' no campo 'descricao_comorbidade'
            responsavel_id=None,  # Adicione o responsável, se necessário
            empresa_id=None  # Adicione a empresa, se necessário
        )

        # Se o aluno for menor de 18, associe o responsável
        if idade < 18:
            # Aqui você pode adicionar a lógica para salvar o responsável no banco, caso o responsável seja informado.
            # Exemplo de adição do responsável:
            responsavel = Responsavel(
                nome=data['nomeResponsavel'],
                sobrenome=data['sobrenomeResponsavel'],
                parentesco=data['parentescoResponsavel']
            )
            db.session.add(responsavel)
            aluno.responsavel_id = responsavel.id

        # Se o aluno for empregado, associe a empresa
        if empregado == 'sim':
            # Aqui você pode adicionar a lógica para salvar a empresa no banco, caso a empresa seja informada.
            # Exemplo de adição da empresa:
            empresa = Empresa(
                nome=data['empresa'],
                endereco=data.get('endereco_empresa'),
                telefone=data.get('telefone_empresa')
            )
            db.session.add(empresa)
            aluno.empresa_id = empresa.id

        # Se o aluno enviar uma foto, salve-a
        if 'foto' in request.files:
            foto = request.files['foto']
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            foto_path = os.path.join(upload_dir, foto.filename)
            foto.save(foto_path)
            aluno.foto = foto_path

        # Adicionando e fazendo o commit no banco
        db.session.add(aluno)
        db.session.commit()

        return jsonify({'mensagem': 'Cadastro realizado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar aluno', 'detalhes': str(e)}), 500
