from flask import Blueprint, request, jsonify
from datetime import datetime

from app.extensions import db
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno

ocorrencia_bp = Blueprint('ocorrencias', __name__, url_prefix='/ocorrencias')


def _parse_date_yyyy_mm_dd(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        return None


@ocorrencia_bp.route("/tipos", methods=["GET"])
def tipos_ocorrencias():
    return jsonify({"tipos": Ocorrencia.get_tipos()}), 200


@ocorrencia_bp.route("/", methods=["POST"])
def criar_ocorrencia():
    """
    Cria ocorrência.
    ✅ turma_id é preenchido automaticamente com aluno.turma_id (se existir).
    """
    data = request.get_json(silent=True) or {}

    aluno_id = data.get("aluno_id")
    tipo = (data.get("tipo") or "").strip()
    descricao = (data.get("descricao") or "").strip()
    data_ocorrencia = _parse_date_yyyy_mm_dd(data.get("data_ocorrencia"))

    if not aluno_id:
        return jsonify({"erro": "aluno_id é obrigatório"}), 400
    if not tipo:
        return jsonify({"erro": "tipo é obrigatório"}), 400
    if not descricao:
        return jsonify({"erro": "descricao é obrigatória"}), 400

    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404

    # ✅ pega turma automaticamente do aluno
    turma_id = getattr(aluno, "turma_id", None)

    oc = Ocorrencia(
        aluno_id=aluno.id,
        tipo=tipo,
        descricao=descricao,
        data=datetime.utcnow(),
        data_ocorrencia=data_ocorrencia,
        turma_id=turma_id  # pode ser None (agora permitido)
    )

    db.session.add(oc)
    db.session.commit()

    return jsonify({
        "mensagem": "Ocorrência cadastrada com sucesso!",
        "ocorrencia": oc.to_dict()
    }), 201


@ocorrencia_bp.route('/listar', methods=['GET'])
def listar_ocorrencias():
    aluno_id = request.args.get('aluno_id')

    try:
        if aluno_id:
            ocorrencias = Ocorrencia.query.filter_by(aluno_id=aluno_id).order_by(Ocorrencia.id.desc()).all()
        else:
            ocorrencias = Ocorrencia.query.order_by(Ocorrencia.id.desc()).all()

        return jsonify([oc.to_dict() for oc in ocorrencias]), 200

    except Exception as e:
        return jsonify({'erro': 'Erro ao listar ocorrências', 'detalhes': str(e)}), 500
