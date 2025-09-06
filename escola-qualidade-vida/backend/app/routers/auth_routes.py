from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from app.models.usuario import Usuario
from app.extensions import db
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask_cors import cross_origin

# Blueprint para autenticação
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@cross_origin()
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

@auth_bp.route('/recuperar_senha', methods=['POST', 'OPTIONS'])
@cross_origin()
def recuperar_senha():
    try:
        current_app.logger.info("Rota /recuperar_senha acessada")
        
        # Verificar se há dados JSON
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Dados JSON necessários'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
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
        
        # Enviar email de recuperação (substitui o log antigo)
        enviar_email_recuperacao(email, token)
        
        return jsonify({
            'success': True, 
            'message': 'Link de recuperação enviado para seu e-mail'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro em recuperar_senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# ROTA QUE ESTAVA FALTANDO - ADICIONE ESTA ROTA
@auth_bp.route('/redefinir_senha/<token>', methods=['PUT', 'OPTIONS'])
@cross_origin()
def redefinir_senha(token):
    try:
        current_app.logger.info(f"Tentativa de redefinir senha com token: {token}")
        
        # Verificar se há dados JSON
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Dados JSON necessários'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        nova_senha = data.get('nova_senha')
        confirmar_senha = data.get('confirmar_senha')
        
        if not nova_senha or not confirmar_senha:
            return jsonify({'success': False, 'message': 'Senha é obrigatória'}), 400
        
        if nova_senha != confirmar_senha:
            return jsonify({'success': False, 'message': 'Senhas não coincidem'}), 400
        
        # Buscar usuário pelo token
        usuario = Usuario.query.filter_by(token_recuperacao=token).first()
        
        if not usuario:
            current_app.logger.warning(f"Token não encontrado: {token}")
            return jsonify({'success': False, 'message': 'Token inválido ou expirado'}), 400
        
        if usuario.token_expiracao < datetime.utcnow():
            current_app.logger.warning(f"Token expirado: {token}")
            return jsonify({'success': False, 'message': 'Token expirado'}), 400
        
        # Hash da nova senha
        usuario.senha = generate_password_hash(nova_senha)
        usuario.token_recuperacao = None
        usuario.token_expiracao = None
        db.session.commit()
        
        current_app.logger.info(f"Senha redefinida com sucesso para: {usuario.email}")
        return jsonify({'success': True, 'message': 'Senha redefinida com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro em redefinir_senha: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# FUNÇÃO PARA ENVIAR EMAIL DE RECUPERAÇÃO (ADICIONADA)
def enviar_email_recuperacao(email, token):
    """Função para enviar email de recuperação"""
    try:
        # Configurações do email
        smtp_server = current_app.config.get('SMTP_SERVER')
        smtp_port = current_app.config.get('SMTP_PORT', 587)
        email_from = current_app.config.get('EMAIL_FROM')
        email_password = current_app.config.get('EMAIL_PASSWORD')
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:8080')
        
        # Se não tiver configurações de SMTP, apenas logue (modo desenvolvimento)
        if not all([smtp_server, email_from, email_password]):
            current_app.logger.info(f"🔐 Token de recuperação para {email}: {token}")
            current_app.logger.info(f"🌐 Link: {frontend_url}/redefinir_senha.html?token={token}")
            return
        
        # Link para redefinição
        link = f"{frontend_url}/redefinir_senha.html?token={token}"
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email
        msg['Subject'] = 'Recuperação de Senha - Sistema Escolar'
        
        # Corpo do email em HTML
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ padding: 30px; background-color: #f9f9f9; border: 1px solid #ddd; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; 
                         color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                .code {{ background-color: #f4f4f4; padding: 10px; border-radius: 4px; font-family: monospace; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Recuperação de Senha</h1>
                </div>
                <div class="content">
                    <p>Olá,</p>
                    <p>Você solicitou a recuperação de senha para sua conta no <strong>Sistema de Qualidade de Vida Escolar</strong>.</p>
                    
                    <p style="text-align: center;">
                        <a href="{link}" class="button">🔄 Redefinir Senha</a>
                    </p>
                    
                    <p>Se o botão não funcionar, copie e cole este link no seu navegador:</p>
                    <p class="code">{link}</p>
                    
                    <p><strong>⏰ Importante:</strong> Este link expira em 1 hora por motivos de segurança.</p>
                    
                    <p>Se você não solicitou esta recuperação, ignore este email - sua senha permanecerá inalterada.</p>
                    
                    <p>Atenciosamente,<br>
                    <strong>Equipe do Sistema Escolar</strong><br>
                    SENAI - Serviço Nacional de Aprendizagem Industrial</p>
                </div>
                <div class="footer">
                    <p>Este é um email automático, por favor não responda.</p>
                    <p>© 2024 Sistema de Qualidade de Vida Escolar. Todos os direitos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Enviar email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
        server.quit()
        
        current_app.logger.info(f"✅ Email de recuperação enviado para: {email}")
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao enviar email para {email}: {e}")
        # Não levanta exceção para não quebrar o fluxo principal

# Rota simplificada para teste
@auth_bp.route('/recuperar_senha_test', methods=['POST'])
@cross_origin()
def recuperar_senha_test():
    """Rota simplificada para testar se o backend está funcionando"""
    try:
        return jsonify({
            'success': True, 
            'message': 'Rota de teste funcionando!'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/test', methods=['GET'])
@cross_origin()
def test_route():
    """Rota de teste para verificar se o blueprint está funcionando"""
    return jsonify({'message': 'Rota de autenticação funcionando!', 'status': 'success'}), 200

# Rotas adicionais para teste das novas funcionalidades
@auth_bp.route('/test_redefinir', methods=['GET'])
@cross_origin()
def test_redefinir():
    """Rota de teste para verificar se o endpoint está acessível"""
    return jsonify({'message': 'Rota de redefinição está funcionando!', 'method': 'GET'}), 200

@auth_bp.route('/test_redefinir_post', methods=['POST'])
@cross_origin()
def test_redefinir_post():
    """Rota de teste para verificar POST"""
    return jsonify({'message': 'Rota POST de redefinição está funcionando!', 'method': 'POST'}), 200