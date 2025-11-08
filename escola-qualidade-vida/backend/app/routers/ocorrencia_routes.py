# app/routers/ocorrencia_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from app.extensions import db
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno

# aceita /ocorrencias e /ocorrencias/
ocorrencia_bp = Blueprint("ocorrencias", __name__, url_prefix="/ocorrencias")
ocorrencia_bp.url_defaults = {}
ocorrencia_bp.url_value_preprocessor = None

def _get_payload():
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data
    return request.form.to_dict()

# ---------- CREATE ----------
@ocorrencia_bp.route("", methods=["POST"])      # /ocorrencias
@ocorrencia_bp.route("/", methods=["POST"])     # /ocorrencias/
def criar_ocorrencia():
    """
    Cadastra uma ocorrência.
    Espera JSON ou form-data com: aluno_id (int), tipo (str), descricao (str),
    opcional data_ocorrencia = 'YYYY-MM-DD'
    """
    data = _get_payload() or {}
    required = ("aluno_id", "tipo", "descricao")
    faltando = [k for k in required if not data.get(k)]
    if faltando:
        return jsonify({"erro": "Preencha todos os campos obrigatórios.", "campos_faltando": faltando}), 400

    # valida aluno
    try:
        aluno_id = int(str(data["aluno_id"]).strip())
    except (TypeError, ValueError):
        return jsonify({"erro": "aluno_id inválido."}), 400

    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado."}), 404

    # data_ocorrencia opcional (default: hoje)
    data_txt = (data.get("data_ocorrencia") or "").strip()
    if data_txt:
        try:
            data_ocorrencia = datetime.strptime(data_txt, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"erro": "Formato inválido para data_ocorrencia. Use YYYY-MM-DD."}), 400
    else:
        data_ocorrencia = date.today()

    try:
        oc = Ocorrencia(
            aluno_id=aluno_id,
            tipo=data["tipo"].strip(),
            descricao=data["descricao"].strip(),
            data_ocorrencia=data_ocorrencia,
        )
        db.session.add(oc)
        db.session.commit()
        return jsonify({
            "mensagem": "Ocorrência cadastrada com sucesso!",
            "ocorrencia": {
                "id": oc.id,
                "aluno_id": oc.aluno_id,
                "tipo": oc.tipo,
                "descricao": oc.descricao,
                "data_ocorrencia": oc.data_ocorrencia.isoformat() if oc.data_ocorrencia else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao cadastrar ocorrência", "detalhes": str(e)}), 500

# Alias legada: /ocorrencias/cadastrar  (opcional)
@ocorrencia_bp.route("/cadastrar", methods=["POST"])
def criar_ocorrencia_alias():
    return criar_ocorrencia()

# ---------- LIST ----------
@ocorrencia_bp.route("", methods=["GET"])
@ocorrencia_bp.route("/", methods=["GET"])
def listar_ocorrencias():
    """
    Filtros opcionais:
      - aluno_id=<int>
      - data_ini=YYYY-MM-DD
      - data_fim=YYYY-MM-DD
    """
    aluno_id = request.args.get("aluno_id")
    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")

    q = Ocorrencia.query
    if aluno_id:
        try:
            q = q.filter(Ocorrencia.aluno_id == int(aluno_id))
        except ValueError:
            return jsonify({"erro": "aluno_id inválido"}), 400

    def _p(v):
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except Exception:
            return None

    if data_ini:
        di = _p(data_ini)
        if not di:
            return jsonify({"erro": "data_ini inválida (use YYYY-MM-DD)"}), 400
        q = q.filter(Ocorrencia.data_ocorrencia >= di)

    if data_fim:
        df = _p(data_fim)
        if not df:
            return jsonify({"erro": "data_fim inválida (use YYYY-MM-DD)"}), 400
        q = q.filter(Ocorrencia.data_ocorrencia <= df)

    itens = q.order_by(Ocorrencia.id.desc()).all()
    return jsonify([{
        "id": o.id,
        "aluno_id": o.aluno_id,
        "tipo": o.tipo,
        "descricao": o.descricao,
        "data_ocorrencia": o.data_ocorrencia.isoformat() if o.data_ocorrencia else None
    } for o in itens]), 200
