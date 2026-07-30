import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.usuario import Usuario


auth_bp = Blueprint("auth", __name__)
RECOVERY_MESSAGE = "Se o e-mail existir em nosso sistema, voce recebera um link de recuperacao."


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha")

    if not email or not senha:
        return jsonify({"erro": "E-mail e senha sao obrigatorios"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({"erro": "Credenciais invalidas"}), 401

    access_token = create_access_token(identity=str(usuario.id))
    return jsonify({
        "access_token": access_token,
        "user_id": usuario.id,
        "cargo": usuario.cargo,
    }), 200


@auth_bp.route("/recuperar_senha", methods=["POST", "OPTIONS"])
def recuperar_senha():
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()

        if not email:
            return jsonify({"success": False, "message": "E-mail e obrigatorio"}), 400

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            token = secrets.token_urlsafe(32)
            usuario.token_recuperacao = token
            usuario.token_expiracao = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            enviar_email_recuperacao(email, token)

        return jsonify({"success": True, "message": RECOVERY_MESSAGE}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro em recuperar_senha: %s", e, exc_info=True)
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500


@auth_bp.route("/redefinir_senha/<token>", methods=["PUT", "OPTIONS"])
def redefinir_senha(token):
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(silent=True) or {}
        nova_senha = data.get("nova_senha")
        confirmar_senha = data.get("confirmar_senha")

        if not nova_senha or not confirmar_senha:
            return jsonify({"success": False, "message": "Senha e obrigatoria"}), 400
        if nova_senha != confirmar_senha:
            return jsonify({"success": False, "message": "Senhas nao coincidem"}), 400
        if len(nova_senha) < 8:
            return jsonify({"success": False, "message": "A senha deve ter pelo menos 8 caracteres"}), 400

        usuario = Usuario.query.filter_by(token_recuperacao=token).first()
        if not usuario or not usuario.token_expiracao:
            return jsonify({"success": False, "message": "Token invalido ou expirado"}), 400
        if usuario.token_expiracao < datetime.utcnow():
            usuario.token_recuperacao = None
            usuario.token_expiracao = None
            db.session.commit()
            return jsonify({"success": False, "message": "Token invalido ou expirado"}), 400

        usuario.senha = generate_password_hash(nova_senha)
        usuario.token_recuperacao = None
        usuario.token_expiracao = None
        db.session.commit()

        current_app.logger.info("Senha redefinida com sucesso para usuario id=%s", usuario.id)
        return jsonify({"success": True, "message": "Senha redefinida com sucesso"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Erro em redefinir_senha: %s", e, exc_info=True)
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500


def enviar_email_recuperacao(email, token):
    smtp_server = current_app.config.get("SMTP_SERVER")
    smtp_port = current_app.config.get("SMTP_PORT", 587)
    email_from = current_app.config.get("EMAIL_FROM")
    email_password = current_app.config.get("EMAIL_PASSWORD")
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:8080")

    if not all([smtp_server, email_from, email_password]):
        current_app.logger.warning("SMTP nao configurado; email de recuperacao nao enviado para %s", email)
        if os.environ.get("ALLOW_PASSWORD_RESET_TOKEN_LOG") == "1":
            current_app.logger.warning(
                "Link de recuperacao habilitado explicitamente para desenvolvimento: %s/redefinir_senha.html?token=%s",
                frontend_url,
                token,
            )
        return False

    link = f"{frontend_url}/redefinir_senha.html?token={token}"
    msg = MIMEMultipart()
    msg["From"] = email_from
    msg["To"] = email
    msg["Subject"] = "Recuperacao de Senha - Sistema Escolar"

    body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
      <h1>Recuperacao de Senha</h1>
      <p>Voce solicitou a recuperacao de senha para sua conta no Sistema de Qualidade de Vida Escolar.</p>
      <p><a href="{link}">Redefinir senha</a></p>
      <p>Se o link nao abrir, copie e cole no navegador:</p>
      <p style="word-break: break-all;">{link}</p>
      <p>Este link expira em 1 hora.</p>
      <p>Se voce nao solicitou esta recuperacao, ignore este email.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_from, email_password)
            server.send_message(msg)
        current_app.logger.info("Email de recuperacao enviado para %s", email)
        return True
    except Exception as e:
        current_app.logger.error("Erro ao enviar email de recuperacao para %s: %s", email, e, exc_info=True)
        return False
