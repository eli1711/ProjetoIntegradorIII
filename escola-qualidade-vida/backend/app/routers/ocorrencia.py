from flask import Blueprint, request, jsonify
from app import db
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno

ocorrencia_bp = Blueprint('ocorrencias', __name__, url_prefix='/ocorrencias')

@ocorrencia_bp.route('/listar', methods=['GET'])
def listar_ocorrencias():
    aluno_id = request.args.get('aluno_id')

    try:
        if aluno_id:
            ocorrencias = Ocorrencia.query.filter_by(aluno_id=aluno_id).all()
        else:
            ocorrencias = Ocorrencia.query.all()

        resultado = []
        for oc in ocorrencias:
            resultado.append({
                'id': oc.id,
                'aluno_id': oc.aluno_id,
                'aluno_nome': oc.aluno.nome if oc.aluno else None,
                'tipo': oc.tipo,
                'descricao': oc.descricao,
                'data': oc.data.isoformat(),
                'data_ocorrencia': oc.data_ocorrencia.isoformat() if oc.data_ocorrencia else None
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'erro': 'Erro ao listar ocorrências', 'detalhes': str(e)}), 500
