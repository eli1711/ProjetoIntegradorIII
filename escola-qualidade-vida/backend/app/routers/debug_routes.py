from flask import Blueprint, jsonify
from app.models import Usuario

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/api/debug/users', methods=['GET'])
def debug_users():
    """Endpoint para debug - lista todos os usuários e seus cargos"""
    try:
        users = Usuario.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'nome': user.nome,
                'email': user.email,
                'cargo': user.cargo
            })
        
        return jsonify({
            'total_users': len(users_data),
            'users': users_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500