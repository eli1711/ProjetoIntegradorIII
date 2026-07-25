from flask import Blueprint, jsonify
from app.models import Usuario
from app.services.permission_service import permission_required


debug_bp = Blueprint("debug", __name__)


@debug_bp.route("/api/debug/users", methods=["GET"])
@permission_required("criar_usuario")
def debug_users():
    try:
        users = Usuario.query.order_by(Usuario.id.asc()).all()
        users_data = [
            {
                "id": user.id,
                "nome": user.nome,
                "email": user.email,
                "cargo": user.cargo,
            }
            for user in users
        ]

        return jsonify({"total_users": len(users_data), "users": users_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
