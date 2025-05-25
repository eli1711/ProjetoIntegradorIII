from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia

consulta_aluno_bp = Blueprint('consulta_aluno', __name__)

@consulta_aluno_bp.route('/alunos/buscar', methods=['GET'])
def buscar_alunos():
    nome = request.args.get('nome', '')
    matricula = request.args.get('matricula', '')
    curso = request.args.get('curso', '')

    query = Aluno.query

    if nome:
        query = query.filter(Aluno.nome.ilike(f'%{nome}%'))
    if matricula:
        query = query.filter(Aluno.matricula.ilike(f'%{matricula}%'))
    if curso:
        query = query.filter(Aluno.curso.has(Curso.nome.ilike(f'%{curso}%')))  # Filtro pelo nome do curso

    alunos = query.all()

    if alunos:
        alunos_data = []
        for aluno in alunos:
            alunos_data.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'curso': aluno.curso.nome,  # Incluindo o nome do curso
                'foto': aluno.foto
            })
        
        return jsonify(alunos_data)

    return jsonify({"erro": "Nenhum aluno encontrado."}), 404
