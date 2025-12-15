from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import Usuario


class PermissionService:
    PERMISSIONS = {
        "administrador": {
            "cadastro_aluno": True,
            "ocorrencias": True,
            "relatorios": True,
            "dashboard": True,
            "criar_usuario": True,
            "importar_alunos": True,
            "cadastro_turma": True,
            "consulta_aluno": True,
        },
        "coordenador": {
            "cadastro_aluno": False,
            "ocorrencias": True,
            "relatorios": True,
            "dashboard": True,
            "criar_usuario": False,
            "importar_alunos": True,
            "cadastro_turma": False,
            "consulta_aluno": False,
        },
        "analista": {
            "cadastro_aluno": True,
            "ocorrencias": True,
            "relatorios": False,
            "dashboard": True,
            "criar_usuario": False,
            "importar_alunos": False,
            "cadastro_turma": True,
            "consulta_aluno": True,
        },
    }

    @staticmethod
    def has_permission(cargo: str, pagina: str) -> bool:
        return bool(PermissionService.PERMISSIONS.get(cargo, {}).get(pagina, False))

    @staticmethod
    def get_user_permissions(cargo: str) -> dict:
        return PermissionService.PERMISSIONS.get(cargo, {})


def get_current_user():
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


def permission_required(pagina: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404

            if not PermissionService.has_permission(user.cargo, pagina):
                return jsonify({
                    "error": "Acesso negado",
                    "message": "Você não tem permissão para acessar esta página",
                    "pagina": pagina
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
