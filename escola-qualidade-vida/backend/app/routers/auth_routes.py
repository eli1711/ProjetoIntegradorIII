from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required
from app.models.usuario import Usuario
from app.extensions import db
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Use apenas UM blueprint para todas as rotas de autenticação
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados de login não fornecidos"}), 400

    email = data.get('email')
    senha = data.get('senha')
    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios"}), 400

    # Verifica se usuário existe pelo email
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"erro": "Credenciais inválidas"}), 401

    # Verifica a senha usando hash
    if not check_password_hash(usuario.senha, senha):
        return jsonify({"erro": "Credenciais inválidas"}), 401

    # Gera token JWT de acesso
    access_token = create_access_token(identity=usuario.id)
    return jsonify(access_token=access_token), 200

@auth_bp.route('/recuperar_senha', methods=['POST'])
def recuperar_senha():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'E-mail é obrigatório'}), 400
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario:
            # Por segurança, não revele se o email existe ou não
            return jsonify({
                'success': True, 
                'message': 'Se o e-mail existir em nosso sistema, você receberá um link de recuperação'
            }), 200
        
        # Gerar token de recuperação
        token = secrets.token_urlsafe(32)
        expiracao = datetime.utcnow() + timedelta(hours=1)
        
        # Salvar token no banco
        usuario.token_recuperacao = token
        usuario.token_expiracao = expiracao
        db.session.commit()
        
        # Enviar email
        enviar_email_recuperacao(email, token)
        
        return jsonify({
            'success': True, 
            'message': 'Link de recuperação enviado para seu e-mail'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro em recuperar_senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/redefinir_senha/<token>', methods=['POST'])
def redefinir_senha(token):
    try:
        data = request.get_json()
        nova_senha = data.get('nova_senha')
        confirmar_senha = data.get('confirmar_senha')
        
        if not nova_senha or not confirmar_senha:
            return jsonify({'success': False, 'message': 'Senha é obrigatória'}), 400
        
        if nova_senha != confirmar_senha:
            return jsonify({'success': False, 'message': 'Senhas não coincidem'}), 400
        
        usuario = Usuario.query.filter_by(token_recuperacao=token).first()
        
        if not usuario or usuario.token_expiracao < datetime.utcnow():
            return jsonify({'success': False, 'message': 'Token inválido ou expirado'}), 400
        
        # Hash da nova senha
        usuario.senha = generate_password_hash(nova_senha)
        usuario.token_recuperacao = None
        usuario.token_expiracao = None
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Senha redefinida com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro em redefinir_senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

def enviar_email_recuperacao(email, token):
    """Função para enviar email de recuperação (modo desenvolvimento)"""
    try:
        # Em desenvolvimento, apenas logue o token
        current_app.logger.info(f"🔐 Token de recuperação para {email}: {token}")
        current_app.logger.info(f"🌐 Link: http://localhost:8080/redefinir_senha?token={token}")
        
        # Verifica se as configurações de email existem
        smtp_server = current_app.config.get('SMTP_SERVER')
        if not smtp_server:
            # Modo desenvolvimento - não envia email real
            return
        
        # Modo produção - envia email real
        smtp_port = current_app.config.get('SMTP_PORT', 587)
        email_from = current_app.config.get('EMAIL_FROM')
        email_password = current_app.config.get('EMAIL_PASSWORD')
        
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email
        msg['Subject'] = 'Recuperação de Senha - Sistema Escolar'
        
        link = f"http://localhost:8080/redefinir_senha?token={token}"
        body = f"""
        Olá,
        
        Você solicitou a recuperação de senha. Clique no link abaixo para redefinir sua senha:
        
        {link}
        
        Este link expira em 1 hora.
        
        Se você não solicitou esta recuperação, ignore este email.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
        server.quit()
        
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar email: {e}")