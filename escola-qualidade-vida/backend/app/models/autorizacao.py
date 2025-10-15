def verificar_acesso(cargo, pagina):
    """
    Verifica se um cargo tem acesso a determinada página
    """
    permissoes_por_cargo = {
        'administrador': {
            'principal': True,
            'cadastro_aluno': True,
            'ocorrencias': True,
            'relatorios': True,
            'historico': True,
            'criar_usuario': True,
            'gerenciar_usuarios': True
        },
        'coordenador': {
            'principal': True,
            'cadastro_aluno': False,
            'ocorrencias': False,
            'relatorios': True,
            'historico': True,
            'criar_usuario': False,
            'gerenciar_usuarios': False
        },
        'analista': {
            'principal': True,
            'cadastro_aluno': True,
            'ocorrencias': True,
            'relatorios': False,
            'historico': True,
            'criar_usuario': False,
            'gerenciar_usuarios': False
        }
    }
    
    if cargo in permissoes_por_cargo and pagina in permissoes_por_cargo[cargo]:
        return permissoes_por_cargo[cargo][pagina]
    
    return False