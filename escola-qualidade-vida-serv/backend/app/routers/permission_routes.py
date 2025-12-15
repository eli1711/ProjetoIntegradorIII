from flask import Blueprint, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import Usuario
from app.services.permission_service import PermissionService


permission_bp = Blueprint("permission_bp", __name__)


def _get_user_from_jwt():
    verify_jwt_in_request()
    ident = get_jwt_identity()

    if isinstance(ident, dict):
        user_id = ident.get("id") or ident.get("user_id")
    else:
        user_id = ident

    if not user_id:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return Usuario.query.get(user_id)


@permission_bp.get("/user_permissions")
def user_permissions():
    user = _get_user_from_jwt()
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    perms = PermissionService.get_user_permissions(user.cargo)
    return jsonify({
        "user_id": user.id,
        "cargo": user.cargo,
        "permissions": perms
    }), 200


@permission_bp.get("/check_permission/<string:pagina>")
def check_permission(pagina: str):
    user = _get_user_from_jwt()
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    has_perm = PermissionService.has_permission(user.cargo, pagina)

    if not has_perm:
        return jsonify({
            "has_permission": False,
            "pagina": pagina,
            "cargo": user.cargo
        }), 403

    return jsonify({
        "has_permission": True,
        "pagina": pagina,
        "cargo": user.cargo
    }), 200
