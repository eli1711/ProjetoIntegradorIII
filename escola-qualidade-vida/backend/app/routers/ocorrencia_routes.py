from flask import Blueprint, request, jsonify
from app import db
from app.models.ocorrencia import Ocorrencia
from datetime import datetime


ocorrencia_bp = Blueprint('ocorrencias', __name__, url_prefix='/ocorrencias')
@ocorrencia_bp.route('/cadastrar', methods=['POST'])
def cadastrar_ocorrencia():
    data = request.json

    required_fields = ['aluno_id', 'tipo', 'descricao']
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({'erro':  'Preencha todos os campos obrigatórios'}), 400

    data_ocorrencia = None
    data_recebida = data.get('data_ocorrencia')
    print(f"Recebido data_ocorrencia: {data_recebida}")  # debug

    if data_recebida:
        try:
            data_ocorrencia = datetime.strptime(data_recebida, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'erro': 'Formato inválido para data_ocorrencia. Use YYYY-MM-DD'}), 400

    try:
        ocorrencia = Ocorrencia(
            aluno_id=data['aluno_id'],
            tipo=data['tipo'],
            descricao=data['descricao'],
            data_ocorrencia=data_ocorrencia
        )

        db.session.add(ocorrencia)
        db.session.commit()

        return jsonify({'mensagem': 'Ocorrência cadastrada com sucesso'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar ocorrência', 'detalhes': str(e)}), 500
