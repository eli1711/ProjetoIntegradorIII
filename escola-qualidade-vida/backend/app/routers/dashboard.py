from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia
from app.models.curso import Curso  # Certifique-se de importar o modelo Curso

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('', methods=['GET'])
def dashboard():
    aluno_cpf = request.args.get('aluno')  # Recebe o CPF do aluno
    curso_id = request.args.get('curso')  # Recebe o id do curso
    ocorrencia_tipo = request.args.get('ocorrencia')  # Recebe o tipo de ocorrência

    # Lógica para filtrar alunos com base nos parâmetros
    filters = []
    if aluno_cpf:
        filters.append(Aluno.cpf == aluno_cpf)
    if curso_id:
        filters.append(Aluno.curso_id == curso_id)

    alunos = Aluno.query.filter(*filters).all()

    # Calcular média de idades e PCDs
    media_idades = sum([aluno.idade for aluno in alunos]) / len(alunos) if alunos else 0
    alunos_pcd = sum([1 for aluno in alunos if aluno.pessoa_com_deficiencia])

    # Buscar ocorrências, se necessário
    ocorrencias = Ocorrencia.query.filter(Ocorrencia.tipo == ocorrencia_tipo if ocorrencia_tipo else True).all()

    # Buscar turmas e status das turmas
    turmas_ativas = Curso.query.filter(Curso.status == "Ativa").count()
    turmas_finalizadas = Curso.query.filter(Curso.status == "Finalizada").count()

    return jsonify({
        'mediaIdades': media_idades,
        'alunosPCD': alunos_pcd,
        'turmasAtivas': turmas_ativas,
        'turmasFinalizadas': turmas_finalizadas,
        'ocorrencias': [{
            'tipo': ocorrencia.tipo,
            'descricao': ocorrencia.descricao
        } for ocorrencia in ocorrencias]
    })
