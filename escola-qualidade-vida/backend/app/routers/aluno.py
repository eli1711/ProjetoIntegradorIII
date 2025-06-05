from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia  # Certifique-se de que o modelo de Ocorrência está importado
from app.models.responsavel import Responsavel  # Certifique-se de importar o modelo de Responsável
from sqlalchemy.orm import joinedload  # Usando joinedload para otimizar o carregamento dos relacionamentos

aluno_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

# Alteração na função de resposta da API
@aluno_bp.route('/buscar', methods=['GET'])
def buscar_alunos_por_nome():
    nome = request.args.get('nome', '').strip()
    sobrenome = request.args.get('sobrenome', '').strip()

    filtros = []

    if nome:
        filtros.append(Aluno.nome.ilike(f'%{nome}%'))
    
    if sobrenome:
        filtros.append(Aluno.sobrenome.ilike(f'%{sobrenome}%'))

    if not filtros:
        return jsonify([])

    query = Aluno.query.options(joinedload(Aluno.curso), joinedload(Aluno.responsavel))

    for filtro in filtros:
        query = query.filter(filtro)

    alunos = query.all()

    resultado = []

    for a in alunos:
        ocorrencias = Ocorrencia.query.filter_by(aluno_id=a.id).all()

        sobrenome_completo = a.sobrenome if a.sobrenome else 'Sobrenome não informado'

        # Corrigir a construção do endereço
        endereco = []
        endereco.append(a.rua if a.rua else 'Rua não informada')
        endereco.append(a.bairro if a.bairro else 'Bairro não informado')
        endereco.append(a.cidade if a.cidade else 'Cidade não informada')

        endereco_completo = ', '.join(endereco)

        print(f"Endereço montado para o aluno {a.nome}: {endereco_completo}")  # Debug log

        aluno_data = {
            'id': a.id,
            'nome': f'{a.nome} {sobrenome_completo}',
            'endereco': endereco_completo,  # Aqui garantimos que o endereço estará completo
            'idade': a.idade,
            'empregado': a.empregado,
            'mora_com_quem': a.mora_com_quem or 'Não informado',
            'sobre_aluno': a.sobre_aluno or 'Não informado',
            'foto': a.foto if a.foto else 'Foto não disponível',
            'responsavel_nome': a.responsavel.nome if a.responsavel else 'Não informado',
            'curso': a.curso.nome if a.curso else 'Curso não informado',
            'ocorrencias': [{
                'data_ocorrencia': ocorrencia.data_ocorrencia,
                'tipo': ocorrencia.tipo,
                'descricao': ocorrencia.descricao
            } for ocorrencia in ocorrencias]
        }

        resultado.append(aluno_data)

    return jsonify(resultado)
