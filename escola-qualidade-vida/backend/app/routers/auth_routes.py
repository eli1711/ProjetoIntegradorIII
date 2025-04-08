# app/routes/auth_routes.py
from flask import Blueprint, request, redirect, abort
from app.utils.database import get_db_session
from app.services.auth_service import autenticar_usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    senha = request.form.get("senha")
    db = get_db_session()
    usuario = autenticar_usuario(db, email, senha)
    db.close()
    if not usuario:
        abort(401, "Credenciais inválidas")
    return redirect("/principal.html")
