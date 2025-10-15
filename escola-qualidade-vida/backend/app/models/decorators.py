from functools import wraps
from flask import request, jsonify
import jwt
from app.config import SECRET_KEY
from app.models.enum import Cargo

def cargo_permitido(cargos_permitidos):
    """
    Decorador para restringir o acesso às rotas com base no cargo do usuário.
    Exemplo:
        @cargo_permitido([Cargo.ADMINISTRADOR, Cargo.COORDENADOR])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"erro": "Token ausente"}), 401

            try:
                token = token.replace("Bearer ", "")
                dados = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                cargo_usuario = Cargo.from_str(dados["cargo"])
            except Exception:
                return jsonify({"erro": "Token inválido ou expirado"}), 401

            if cargo_usuario not in cargos_permitidos:
                return jsonify({"erro": "Acesso negado"}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
