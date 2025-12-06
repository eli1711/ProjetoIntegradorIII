from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services.permission_service import PermissionService, get_current_user

permission_bp = Blueprint('permission', __name__)

@permission_bp.route('/check_permission/<pagina>', methods=['GET'])
@jwt_required()
def check_permission(pagina):
    """Verifica se usuário tem permissão para acessar uma página específica"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado ou token inválido'}), 404
        
        has_access = PermissionService.has_permission(user.cargo, pagina)
        
        return jsonify({
            'has_permission': has_access,
            'cargo': user.cargo,
            'pagina': pagina,
            'user_id': user.id
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao verificar permissão: {e}")
        return jsonify({'error': 'Erro ao verificar permissão'}), 500

@permission_bp.route('/user_permissions', methods=['GET'])
@jwt_required()
def get_user_permissions():
    """Retorna todas as permissões do usuário atual"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado ou token inválido'}), 404
        
        permissions = PermissionService.get_user_permissions(user.cargo)
        
        return jsonify({
            'cargo': user.cargo,
            'permissions': permissions,
            'user_id': user.id,
            'nome': user.nome
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao buscar permissões: {e}")
        return jsonify({'error': 'Erro ao buscar permissões'}), 500