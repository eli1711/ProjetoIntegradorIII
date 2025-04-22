# app/controllers/auth_controller.py
from app import db

from flask import Blueprint, request, redirect, render_template, flash, session
from app.services.auth_service import autenticar_usuario
from app.utils.database import db_session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    senha = request.form['senha']
    usuario = autenticar_usuario(db_session, email, senha)

    if not usuario:
        flash("Credenciais inválidas", "danger")
        return redirect('/login.html')
    
    session['usuario_id'] = usuario.id
    return redirect('/principal.html')
