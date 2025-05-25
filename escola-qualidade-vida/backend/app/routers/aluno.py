from flask import Blueprint, request, jsonify
from app.models.aluno import Aluno

aluno_bp = Blueprint('alunos', __name__, url_prefix='/alunos')

@aluno_bp.route('/buscar', methods=['GET'])
def buscar_alunos_por_nome():
    nome = request.args.get('nome', '').strip()
    if not nome:
        return jsonify([])

    alunos = Aluno.query.filter(Aluno.nome.ilike(f'%{nome}%')).all()

    resultado = []
    for a in alunos:
        resultado.append({
            'id': a.id,
            'nome': f'{a.nome} {a.sobrenome}',
            'foto': a.foto if a.foto else ""  # Garante que campo exista no JSON
        })

    return jsonify(resultado)
