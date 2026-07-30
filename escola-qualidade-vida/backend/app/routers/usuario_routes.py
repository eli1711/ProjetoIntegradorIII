from flask import Blueprint, current_app, request, jsonify
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.usuario import Usuario
from app.services.permission_service import permission_required


usuario_bp = Blueprint("usuario_bp", __name__)


@usuario_bp.route("/api/criar_usuario", methods=["POST"])
@permission_required("criar_usuario")
def criar_usuario():
    try:
        data = request.get_json() or {}
        nome = (data.get("nome") or "").strip()
        email = (data.get("email") or "").strip().lower()
        senha = data.get("senha")
        cargo = data.get("cargo")

        if not nome or not email or not senha or not cargo:
            return jsonify({"success": False, "message": "Todos os campos sao obrigatorios"}), 400
        if len(senha) < 8:
            return jsonify({"success": False, "message": "A senha deve ter pelo menos 8 caracteres"}), 400

        if cargo not in ["administrador", "coordenador", "analista"]:
            return jsonify({"success": False, "message": "Cargo invalido"}), 400

        if Usuario.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Usuario ja existe"}), 400

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            cargo=cargo,
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({"success": True, "message": "Usuario criado com sucesso!"}), 201

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao criar usuario")
        return jsonify({"success": False, "message": "Erro ao criar usuario"}), 500


@usuario_bp.route("/api/usuarios", methods=["GET"])
@permission_required("criar_usuario")
def listar_usuarios():
    try:
        usuarios = Usuario.query.order_by(Usuario.nome.asc()).all()
        resultado = [
            {
                "id": u.id,
                "nome": u.nome,
                "email": u.email,
                "cargo": u.cargo,
            }
            for u in usuarios
        ]

        return jsonify({"usuarios": resultado}), 200
    except Exception:
        current_app.logger.exception("Erro ao listar usuarios")
        return jsonify({"error": "Erro ao listar usuarios"}), 500
