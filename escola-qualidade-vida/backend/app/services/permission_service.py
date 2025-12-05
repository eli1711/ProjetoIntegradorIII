from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import Usuario

class PermissionService:
    # Definição das permissões por cargo
    PERMISSIONS = {
        'administrador': {
            'cadastro_aluno': True,
            'ocorrencias': True,
            'relatorios': True,
            'dashboard': True,
            'criar_usuario': True,
            'importar_alunos': True,
            'cadastro_turma': True,
            'consulta_aluno': True
        },
        'coordenador': {
            'cadastro_aluno': False,
            'ocorrencias': True,
            'relatorios': True,
            'dashboard': True,
            'criar_usuario': False,
            'importar_alunos': True,
            'cadastro_turma': False,
            'consulta_aluno': False
        },
        'analista': {
            'cadastro_aluno': True,
            'ocorrencias': True,
            'relatorios': False,
            'dashboard': True,
            'criar_usuario': False,
            'importar_alunos': False,
            'cadastro_turma': True,
            'consulta_aluno': True
        }
    }
    
    @staticmethod
    def has_permission(cargo, pagina):
        """Verifica se um cargo tem permissão para acessar uma página"""
        if cargo in PermissionService.PERMISSIONS:
            return PermissionService.PERMISSIONS[cargo].get(pagina, False)
        return False
    
    @staticmethod
    def get_user_permissions(cargo):
        """Retorna todas as permissões de um cargo"""
        return PermissionService.PERMISSIONS.get(cargo, {})

def get_current_user():
    """Função auxiliar para obter usuário atual com tratamento de erro"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # Garantir que user_id seja inteiro
        if isinstance(user_id, dict):
            # Se for dict, tentar extrair o ID
            user_id = user_id.get('id') or user_id.get('user_id')
        
        user_id = int(user_id) if user_id else None
        
        if not user_id:
            return None
            
        user = Usuario.query.get(user_id)
        return user
        
    except Exception as e:
        print(f"❌ Erro ao obter usuário atual: {e}")
        return None

def permission_required(pagina):
    """Decorator para verificar permissão de acesso a uma página"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({'error': 'Token inválido ou expirado'}), 401
            
            # Verificar permissão
            if not PermissionService.has_permission(user.cargo, pagina):
                return jsonify({
                    'error': 'Acesso negado',
                    'message': 'Você não tem permissão para acessar esta página'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator