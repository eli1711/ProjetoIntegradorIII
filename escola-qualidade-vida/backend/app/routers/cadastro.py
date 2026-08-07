from flask import Blueprint, current_app, jsonify, request

from app.extensions import db
from app.services.aluno_registration_service import (
    StudentRegistrationError,
    register_student_from_form,
)
from app.services.permission_service import permission_required


cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")


@cadastro_bp.route("/alunos", methods=["POST"])
@permission_required("cadastro_aluno")
def cadastrar_aluno():
    """Compatibility endpoint for the legacy student registration form."""
    try:
        aluno = register_student_from_form(
            request.form,
            request.files,
            require_existing_course=False,
            validate_legacy_required=True,
        )
        return jsonify({
            "mensagem": "Aluno cadastrado com sucesso!",
            "id": aluno.id,
            "cpf": aluno.cpf,
            "nome_social": aluno.nome_social,
        }), 201
    except StudentRegistrationError as exc:
        db.session.rollback()
        return jsonify(exc.to_payload()), exc.status_code
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao cadastrar aluno")
        return jsonify({"erro": "Erro ao cadastrar aluno."}), 500
