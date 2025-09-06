from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from app.models.usuario import Usuario
from app.extensions import db
import secrets
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
        
        # Em desenvolvimento, apenas logue o token
        current_app.logger.info(f"Token de recuperação para {email}: {token}")
        current_app.logger.info(f"Link: http://localhost:8080/redefinir_senha.html?token={token}")
        
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