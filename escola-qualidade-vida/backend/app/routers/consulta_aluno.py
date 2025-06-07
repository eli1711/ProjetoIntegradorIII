from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia  # Importando o modelo Ocorrencia
from app.models.curso import Curso

consulta_aluno_bp = Blueprint('consulta_aluno', __name__)

@consulta_aluno_bp.route('/buscar', methods=['GET'])
def buscar_alunos():
    aluno_id = request.args.get('id', None)
    nome = request.args.get('nome', '').strip()

    # Se o ID do aluno for fornecido, busca por ID
    if aluno_id:
        aluno = Aluno.query.options(joinedload(Aluno.curso)).get(aluno_id)  # Usando joinedload para otimizar
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado."}), 404

        # Coleta as ocorrências do aluno
        ocorrencias = Ocorrencia.query.filter_by(aluno_id=aluno.id).all()

        aluno_data = {
            'id': aluno.id,
            'nome': f'{aluno.nome} {aluno.sobrenome}',
            'endereco': f'{aluno.rua}, {aluno.bairro}, {aluno.cidade}',
            'idade': aluno.idade,
            'empregado': aluno.empregado,
            'mora_com_quem': aluno.mora_com_quem,
            'sobre_aluno': aluno.sobre_aluno,
            'foto': aluno.foto if aluno.foto else 'Foto não disponível',
            'responsavel_nome': aluno.responsavel_nome or 'Não informado',
            'curso': aluno.curso.nome if aluno.curso else 'Curso não informado',
            'ocorrencias': [{
                'data_ocorrencia': ocorrencia.data_ocorrencia,
                'tipo': ocorrencia.tipo,
                'descricao': ocorrencia.descricao
            } for ocorrencia in ocorrencias]
        }
        return jsonify(aluno_data)

    # Se o nome for fornecido, busca por nome
    if nome:
        alunos = Aluno.query.filter(Aluno.nome.ilike(f'%{nome}%')).all()
        resultado = []

        for a in alunos:
            # Coleta as ocorrências do aluno
            ocorrencias = Ocorrencia.query.filter_by(aluno_id=a.id).all()

            aluno_data = {
                'id': a.id,
                'nome': f'{a.nome} {a.sobrenome}',
                'endereco': f'{a.rua}, {a.bairro}, {a.cidade}',
                'idade': a.idade,
                'empregado': a.empregado,
                'mora_com_quem': a.mora_com_quem,
                'sobre_aluno': a.sobre_aluno,
                'foto': a.foto if a.foto else 'Foto não disponível',
                'responsavel_nome': a.responsavel_nome or 'Não informado',
                'curso': a.curso.nome if a.curso else 'Curso não informado',
                'ocorrencias': [{
                    'data_ocorrencia': ocorrencia.data_ocorrencia,
                    'tipo': ocorrencia.tipo,
                    'descricao': ocorrencia.descricao
                } for ocorrencia in ocorrencias]
            }
            resultado.append(aluno_data)

        return jsonify(resultado)

    # Se nenhum parâmetro for fornecido, retorna uma lista vazia
    return jsonify([])
