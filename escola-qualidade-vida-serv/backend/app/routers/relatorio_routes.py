from flask import Blueprint, request, jsonify
from .models import Aluno, db  # Importe 'db' aqui

api_bp = Blueprint('api', __name__)

@api_bp.route('/alunos/buscar', methods=['GET'])
def buscar_alunos():
    try:
        # Pega os parâmetros da URL. Usar default='' evita erros se o parâmetro não vier.
        nome_filtro = request.args.get('nome', default='', type=str)
        curso_filtro = request.args.get('curso', default='', type=str)
        ocorrencia_filtro = request.args.get('ocorrencia', default='', type=str)
        turma_filtro = request.args.get('turma', default='', type=str)

        # Inicia uma consulta base no modelo Aluno
        query = Aluno.query

        # CORREÇÃO: Aplicamos o filtro somente se a string do parâmetro não for vazia.
        # Isso garante que um parâmetro vazio (como de um <select> "Todos") não afete a query.
        if nome_filtro:
            query = query.filter(Aluno.nome.ilike(f'%{nome_filtro}%'))

        if curso_filtro:
            query = query.filter(Aluno.curso.ilike(f'%{curso_filtro}%'))

        if ocorrencia_filtro:
            query = query.filter(Aluno.ocorrencia.ilike(f'%{ocorrencia_filtro}%'))

        if turma_filtro:
            query = query.filter(Aluno.turma.ilike(f'%{turma_filtro}%'))

        # Executa a consulta no banco de dados
        alunos_encontrados = query.all()

        # Converte a lista de objetos Aluno para o formato JSON
        resultados = [aluno.to_dict() for aluno in alunos_encontrados]

        return jsonify(resultados)

    except Exception as e:
        # Se algo der errado no servidor, retorna um erro claro
        print(f"Ocorreu um erro: {e}")  # Loga o erro no terminal do backend
        return jsonify({"erro": "Ocorreu um erro interno no servidor"}), 500
