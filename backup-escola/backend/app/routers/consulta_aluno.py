# consulta_aluno.py

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia
from app.models.curso import Curso
from app.models.turma import Turma # Supondo que você tenha um modelo Turma

consulta_aluno_bp = Blueprint('consulta_aluno', __name__, url_prefix='/alunos')

@consulta_aluno_bp.route('/buscar', methods=['GET'])
def buscar_alunos_com_filtros():
    # 1. Captura todos os parâmetros da URL
    nome = request.args.get('nome', '').strip()
    curso_nome = request.args.get('curso', '').strip()
    ocorrencia_tipo = request.args.get('ocorrencia', '').strip()
    turma_nome = request.args.get('turma', '').strip()

    try:
        # 2. Inicia a query base. Usamos 'distinct' para evitar duplicatas 
        #    quando um aluno tem múltiplas ocorrências do mesmo tipo.
        query = Aluno.query.distinct(Aluno.id)

        # 3. Adiciona os filtros dinamicamente
        
        # Filtro por Nome do Aluno
        if nome:
            # ilike faz a busca ser "case-insensitive" (não diferencia maiúsculas de minúsculas)
            query = query.filter(func.concat(Aluno.nome, ' ', Aluno.sobrenome).ilike(f'%{nome}%'))

        # Filtro por Curso
        if curso_nome:
            # Usa 'join' para conectar Aluno com Curso e filtrar pelo nome do curso
            query = query.join(Curso).filter(Curso.nome.ilike(f'%{curso_nome}%'))
        
        # Filtro por Turma
        if turma_nome:
            # Usa 'join' para conectar Aluno com Turma e filtrar pelo nome da turma
            # Nota: Isso assume que você tem um modelo 'Turma' e uma relação em 'Aluno'
            query = query.join(Turma).filter(Turma.nome.ilike(f'%{turma_nome}%'))

        # Filtro por Tipo de Ocorrência
        if ocorrencia_tipo:
            # Usa 'join' para conectar Aluno com Ocorrencia e filtrar pelo tipo
            query = query.join(Ocorrencia).filter(Ocorrencia.tipo.ilike(f'%{ocorrencia_tipo}%'))

        # 4. Executa a query final
        alunos_filtrados = query.all()

        # 5. Formata o resultado para enviar como JSON
        resultado = []
        for aluno in alunos_filtrados:
            ocorrencias_do_aluno = [{
                'data_ocorrencia': oc.data_ocorrencia.isoformat() if oc.data_ocorrencia else None,
                'tipo': oc.tipo,
                'descricao': oc.descricao
            } for oc in aluno.ocorrencias]
            
            resultado.append({
                'id': aluno.id,
                'nome': f'{aluno.nome} {aluno.sobrenome}',
                'curso': aluno.curso.nome if aluno.curso else 'N/A',
                'turma': aluno.turma.nome if hasattr(aluno, 'turma') and aluno.turma else 'N/A', # Exemplo
                'ocorrencias': ocorrencias_do_aluno, # Retorna a lista de ocorrências
            })

        return jsonify(resultado)

    except Exception as e:
        # Em caso de erro, retorna uma mensagem clara
        print(f"Erro na busca: {e}") # Log do erro no console do servidor
        return jsonify({"erro": "Ocorreu um erro ao processar a busca.", "detalhes": str(e)}), 500