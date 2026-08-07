import json
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import func

from app.extensions import db
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia
from app.services.ia_aluno_service import detectar_alertas_ocorrencia
from app.services.permission_service import auth_required, permission_required


ocorrencia_bp = Blueprint("ocorrencias", __name__, url_prefix="/ocorrencias")

STATUS_ACOMPANHAMENTO_VALIDOS = {
    "nao_aplicavel",
    "pendente",
    "em_andamento",
    "concluido",
}


@ocorrencia_bp.route("/tipos", methods=["GET"])
@auth_required()
def listar_tipos():
    try:
        return jsonify({"tipos": Ocorrencia.get_tipos()}), 200
    except Exception as e:
        current_app.logger.error("Erro ao listar tipos de ocorrencia: %s", e, exc_info=True)
        return jsonify({"erro": "Erro ao listar tipos"}), 500


@ocorrencia_bp.route("/", methods=["POST"])
@permission_required("ocorrencias")
def cadastrar_ocorrencia():
    try:
        dados = request.get_json(silent=True) or {}

        if not dados.get("aluno_id"):
            return jsonify({"erro": "ID do aluno e obrigatorio"}), 400
        if not dados.get("tipo"):
            return jsonify({"erro": "Tipo de ocorrencia e obrigatorio"}), 400
        if not dados.get("descricao"):
            return jsonify({"erro": "Descricao e obrigatoria"}), 400

        aluno = Aluno.query.get(dados["aluno_id"])
        if not aluno:
            return jsonify({"erro": "Aluno nao encontrado"}), 404
        if not aluno.turma_id:
            return jsonify({"erro": "Aluno nao esta vinculado a uma turma"}), 400

        tipo = dados["tipo"]
        tipos_validos = Ocorrencia.get_tipos()
        if tipo not in tipos_validos:
            return jsonify({"erro": f"Tipo invalido. Tipos validos: {', '.join(tipos_validos)}"}), 400

        data_ocorrencia = None
        if dados.get("data_ocorrencia"):
            try:
                data_ocorrencia = datetime.strptime(dados["data_ocorrencia"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"erro": "Formato de data invalido. Use YYYY-MM-DD"}), 400

        alerta = detectar_alertas_ocorrencia(tipo, dados["descricao"], dados.get("data_ocorrencia"))
        acompanhamento_payload, validation_error = _build_acompanhamento_payload(dados, alerta)
        if validation_error:
            return jsonify(validation_error), 400

        nova_ocorrencia = Ocorrencia(
            aluno_id=dados["aluno_id"],
            tipo=tipo,
            descricao=dados["descricao"],
            data_ocorrencia=data_ocorrencia,
            turma_id=aluno.turma_id,
            **acompanhamento_payload,
        )
        db.session.add(nova_ocorrencia)
        db.session.commit()

        return jsonify({
            "mensagem": "Ocorrencia cadastrada com sucesso",
            "ocorrencia_id": nova_ocorrencia.id,
            "alerta_sensivel": nova_ocorrencia.alerta_sensivel,
            "ocorrencia": nova_ocorrencia.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao cadastrar ocorrencia: %s", e, exc_info=True)
        return jsonify({"erro": "Erro ao cadastrar ocorrencia"}), 500


@ocorrencia_bp.route("/listar", methods=["GET"])
@permission_required("ocorrencias")
def listar_ocorrencias_compat():
    return listar_todas_ocorrencias()


@ocorrencia_bp.route("/sensiveis", methods=["GET"])
@permission_required("ocorrencias")
def listar_ocorrencias_sensiveis():
    status = (request.args.get("status") or "abertos").strip().lower()
    nivel = (request.args.get("nivel") or "todos").strip().lower()
    tipo_alerta = (request.args.get("tipo_alerta") or "todos").strip().lower()

    try:
        query = Ocorrencia.query.filter(Ocorrencia.alerta_sensivel.is_(True))

        if status == "abertos":
            query = query.filter(Ocorrencia.status_acompanhamento != "concluido")
        elif status != "todos":
            if status not in STATUS_ACOMPANHAMENTO_VALIDOS:
                return jsonify({"erro": "status invalido"}), 400
            query = query.filter(Ocorrencia.status_acompanhamento == status)

        if nivel != "todos":
            query = query.filter(Ocorrencia.alerta_sensivel_nivel == nivel)

        if tipo_alerta != "todos":
            query = query.filter(Ocorrencia.alerta_sensivel_tipo == tipo_alerta)

        ocorrencias = (
            query
            .order_by(
                Ocorrencia.status_acompanhamento.asc(),
                Ocorrencia.data_acompanhamento.asc().nullslast(),
                Ocorrencia.data.desc(),
            )
            .all()
        )

        return jsonify({
            "totais": _totais_ocorrencias_sensiveis(),
            "filtros": {
                "status": status,
                "nivel": nivel,
                "tipo_alerta": tipo_alerta,
            },
            "ocorrencias": [ocorrencia.to_dict() for ocorrencia in ocorrencias],
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao listar ocorrencias sensiveis: %s", e, exc_info=True)
        return jsonify({"erro": "Erro ao listar ocorrencias sensiveis"}), 500


@ocorrencia_bp.route("/sensiveis/sincronizar", methods=["POST"])
@permission_required("ocorrencias")
def sincronizar_ocorrencias_sensiveis():
    try:
        total_atualizadas = _sync_ocorrencias_sensiveis_existentes()
        return jsonify({
            "mensagem": "Ocorrencias sensiveis sincronizadas com sucesso",
            "atualizadas": total_atualizadas,
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao sincronizar ocorrencias sensiveis: %s", e, exc_info=True)
        return jsonify({"erro": "Erro ao sincronizar ocorrencias sensiveis"}), 500


@ocorrencia_bp.route("/", methods=["GET"])
@permission_required("ocorrencias")
def listar_todas_ocorrencias():
    aluno_id = request.args.get("aluno_id")
    turma_id = request.args.get("turma_id")
    tipo = request.args.get("tipo")
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    try:
        query = Ocorrencia.query

        if aluno_id:
            query = query.filter_by(aluno_id=aluno_id)
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
        if tipo:
            query = query.filter_by(tipo=tipo)
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
                query = query.filter(Ocorrencia.data_ocorrencia >= data_inicio_dt)
            except ValueError:
                return jsonify({"erro": "Formato de data_inicio invalido. Use YYYY-MM-DD"}), 400
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
                query = query.filter(Ocorrencia.data_ocorrencia <= data_fim_dt)
            except ValueError:
                return jsonify({"erro": "Formato de data_fim invalido. Use YYYY-MM-DD"}), 400

        ocorrencias = query.order_by(Ocorrencia.data.desc()).all()
        return jsonify([ocorrencia.to_dict() for ocorrencia in ocorrencias]), 200

    except Exception as e:
        current_app.logger.error("Erro ao listar ocorrencias: %s", e, exc_info=True)
        return jsonify({"erro": "Erro ao listar ocorrencias"}), 500


@ocorrencia_bp.route("/<int:id>", methods=["GET"])
@permission_required("ocorrencias")
def obter_ocorrencia(id):
    ocorrencia = Ocorrencia.query.get(id)
    if not ocorrencia:
        return jsonify({"erro": "Ocorrencia nao encontrada"}), 404
    return jsonify(ocorrencia.to_dict()), 200


@ocorrencia_bp.route("/<int:id>", methods=["PUT"])
@permission_required("ocorrencias")
def atualizar_ocorrencia(id):
    try:
        ocorrencia = Ocorrencia.query.get(id)
        if not ocorrencia:
            return jsonify({"erro": "Ocorrencia nao encontrada"}), 404

        dados = request.get_json(silent=True) or {}
        if dados.get("tipo") and dados["tipo"] not in Ocorrencia.get_tipos():
            return jsonify({"erro": "Tipo de ocorrencia invalido"}), 400

        if "tipo" in dados:
            ocorrencia.tipo = dados["tipo"]
        if "descricao" in dados:
            ocorrencia.descricao = dados["descricao"]
        if "data_ocorrencia" in dados:
            ocorrencia.data_ocorrencia = (
                datetime.strptime(dados["data_ocorrencia"], "%Y-%m-%d").date()
                if dados["data_ocorrencia"]
                else None
            )

        alerta = detectar_alertas_ocorrencia(
            ocorrencia.tipo,
            ocorrencia.descricao,
            ocorrencia.data_ocorrencia.isoformat() if ocorrencia.data_ocorrencia else None,
        )
        acompanhamento_payload, validation_error = _build_acompanhamento_payload(
            dados,
            alerta,
            ocorrencia=ocorrencia,
        )
        if validation_error:
            return jsonify(validation_error), 400

        for field, value in acompanhamento_payload.items():
            setattr(ocorrencia, field, value)

        db.session.commit()
        return jsonify({
            "mensagem": "Ocorrencia atualizada com sucesso",
            "ocorrencia": ocorrencia.to_dict(),
        }), 200

    except ValueError:
        db.session.rollback()
        return jsonify({"erro": "Formato de data invalido. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao atualizar ocorrencia: %s", e, exc_info=True)
        return jsonify({"erro": "Erro ao atualizar ocorrencia"}), 500


@ocorrencia_bp.route("/<int:id>", methods=["DELETE"])
@permission_required("ocorrencias")
def excluir_ocorrencia(id):
    try:
        ocorrencia = Ocorrencia.query.get(id)
        if not ocorrencia:
            return jsonify({"erro": "Ocorrencia nao encontrada"}), 404

        db.session.delete(ocorrencia)
        db.session.commit()
        return jsonify({"mensagem": "Ocorrencia excluida com sucesso"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro ao excluir ocorrencia: %s", e, exc_info=True)
        return jsonify({"erro": "Erro ao excluir ocorrencia"}), 500


def _build_acompanhamento_payload(dados, alerta, ocorrencia=None):
    is_sensitive = alerta["ativo"]
    action = _clean_text(dados.get("acao_tomada", getattr(ocorrencia, "acao_tomada", "")))
    follow_up = _clean_text(dados.get("acompanhamento", getattr(ocorrencia, "acompanhamento", "")))

    follow_up_date_value = dados.get(
        "data_acompanhamento",
        getattr(ocorrencia, "data_acompanhamento", None),
    )
    follow_up_date, date_error = _parse_optional_date(follow_up_date_value)
    if date_error:
        return None, {"erro": "Formato de data_acompanhamento invalido. Use YYYY-MM-DD"}

    status = _clean_text(dados.get(
        "status_acompanhamento",
        getattr(ocorrencia, "status_acompanhamento", None),
    ))

    if is_sensitive:
        missing = []
        if not action:
            missing.append("acao_tomada")
        if not follow_up:
            missing.append("acompanhamento")
        if not follow_up_date:
            missing.append("data_acompanhamento")

        if missing:
            return None, {
                "erro": (
                    "Ocorrencia com assunto sensivel exige acao tomada, "
                    "acompanhamento e data de acompanhamento."
                ),
                "tema_sensivel": True,
                "alerta": alerta,
                "campos_obrigatorios": missing,
            }

        status = status or "pendente"
        if status == "nao_aplicavel":
            status = "pendente"
    else:
        status = status or "nao_aplicavel"

    if status not in STATUS_ACOMPANHAMENTO_VALIDOS:
        return None, {
            "erro": (
                "status_acompanhamento invalido. Use: "
                + ", ".join(sorted(STATUS_ACOMPANHAMENTO_VALIDOS))
            )
        }

    return {
        "alerta_sensivel": is_sensitive,
        "alerta_sensivel_tipo": alerta["tipo"] if is_sensitive else None,
        "alerta_sensivel_nivel": alerta["nivel"] if is_sensitive else None,
        "alerta_sensivel_motivos": (
            json.dumps(alerta["motivos"], ensure_ascii=False)
            if is_sensitive
            else None
        ),
        "acao_tomada": action or None,
        "acompanhamento": follow_up or None,
        "data_acompanhamento": follow_up_date,
        "status_acompanhamento": status,
    }, None


def _clean_text(value):
    return str(value or "").strip()


def _parse_optional_date(value):
    if not value:
        return None, None
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value, None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date(), None
    except ValueError:
        return None, True


def _sync_ocorrencias_sensiveis_existentes():
    updated_count = 0
    for ocorrencia in Ocorrencia.query.all():
        if _sync_alerta_sensivel(ocorrencia):
            updated_count += 1

    if updated_count:
        db.session.commit()
    return updated_count


def _sync_alerta_sensivel(ocorrencia):
    alerta = detectar_alertas_ocorrencia(
        ocorrencia.tipo,
        ocorrencia.descricao,
        ocorrencia.data_ocorrencia.isoformat() if ocorrencia.data_ocorrencia else None,
    )

    is_sensitive = alerta["ativo"]
    values = {
        "alerta_sensivel": is_sensitive,
        "alerta_sensivel_tipo": alerta["tipo"] if is_sensitive else None,
        "alerta_sensivel_nivel": alerta["nivel"] if is_sensitive else None,
        "alerta_sensivel_motivos": (
            json.dumps(alerta["motivos"], ensure_ascii=False)
            if is_sensitive
            else None
        ),
    }

    if is_sensitive:
        status = ocorrencia.status_acompanhamento
        if not status or status == "nao_aplicavel":
            values["status_acompanhamento"] = "pendente"
    elif not (
        ocorrencia.acao_tomada
        or ocorrencia.acompanhamento
        or ocorrencia.data_acompanhamento
    ):
        values["status_acompanhamento"] = "nao_aplicavel"

    updated = False
    for field, value in values.items():
        if getattr(ocorrencia, field) != value:
            setattr(ocorrencia, field, value)
            updated = True

    return updated


def _totais_ocorrencias_sensiveis():
    base_filter = Ocorrencia.alerta_sensivel.is_(True)
    status_counts = dict(
        db.session.query(Ocorrencia.status_acompanhamento, func.count(Ocorrencia.id))
        .filter(base_filter)
        .group_by(Ocorrencia.status_acompanhamento)
        .all()
    )
    level_counts = dict(
        db.session.query(Ocorrencia.alerta_sensivel_nivel, func.count(Ocorrencia.id))
        .filter(base_filter)
        .group_by(Ocorrencia.alerta_sensivel_nivel)
        .all()
    )

    totais = {
        "total": sum(status_counts.values()),
        "pendente": int(status_counts.get("pendente", 0)),
        "em_andamento": int(status_counts.get("em_andamento", 0)),
        "concluido": int(status_counts.get("concluido", 0)),
        "critico": int(level_counts.get("critico", 0)),
        "atencao": int(level_counts.get("atencao", 0)),
    }
    totais["abertos"] = totais["pendente"] + totais["em_andamento"]
    return totais
