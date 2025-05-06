from flask import Blueprint, request, jsonify
from app.models.ocorrencia import Ocorrencia
from app.models.usuario import Usuario
from app.models.aluno import Aluno
from app.utils.database import db

ocorrencia_bp = Blueprint('ocorrencia', __name__, url_prefix='/ocorrencias')

@ocorrencia_bp.route('/registrar', methods=['POST'])
def registrar_ocorrencia():
    try:
        # Recebe os dados do formulário
        data = request.get_json()
        aluno_id = data.get('aluno_id')
        tipo = data.get('tipo')
        descricao = data.get('descricao')
        usuario_id = data.get('usuario_id')

        # Valida os dados recebidos
        if not aluno_id or not tipo or not descricao:
            return jsonify({"erro": "Dados incompletos!"}), 400

        # Verifica se o aluno existe
        aluno = Aluno.query.filter_by(id=aluno_id).first()
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado!"}), 404

        # Cria a nova ocorrência
        nova_ocorrencia = Ocorrencia(
            aluno_id=aluno_id,
            tipo=tipo,
            descricao=descricao,
            usuario_id=usuario_id
        )

        # Salva no banco de dados
        db.session.add(nova_ocorrencia)
        db.session.commit()

        return jsonify({"mensagem": "Ocorrência registrada com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500
