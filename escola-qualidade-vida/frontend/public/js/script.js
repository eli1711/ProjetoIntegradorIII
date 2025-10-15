document.addEventListener('DOMContentLoaded', async function () {
    const logoutBtn = document.getElementById('logoutBtn');

    // Verifica se o usuário está logado
    if (!localStorage.getItem('access_token')) {
        window.location.href = 'index.html';
        return;
    }

    // Função de logout
    logoutBtn && logoutBtn.addEventListener('click', logout);

    // ------------------- BLOQUEIO DE LINKS POR CARGO -------------------
    try {
        const cargo = localStorage.getItem('cargo');
        console.log('Cargo do usuário:', cargo); // DEBUG

        if (!cargo) {
            console.error('Cargo não encontrado no localStorage');
            return;
        }

        // Mapeamento de IDs dos links para as páginas
        const mapeamento_links = {
            'link-cadastro-aluno': 'cadastro_aluno',
            'link-ocorrencias': 'ocorrencias', 
            'link-relatorios': 'relatorios',
            'link-historico': 'historico',
            'link-criar-usuario': 'criar_usuario',
            'link-gerenciar-usuarios': 'gerenciar_usuarios'
        };

        console.log('Aplicando restrições para cargo:', cargo);

        // Para cada link, verificar se o cargo tem permissão
        Object.keys(mapeamento_links).forEach(linkId => {
            const link = document.getElementById(linkId);
            if (link) {
                const pagina = mapeamento_links[linkId];
                const temAcesso = verificarAcessoLocal(cargo, pagina);
                
                console.log(`Link ${linkId} (${pagina}): ${temAcesso ? 'PERMITIDO' : 'BLOQUEADO'}`);
                
                if (!temAcesso) {
                    link.style.display = 'none';
                } else {
                    link.style.display = 'block'; // Garante que está visível se tem acesso
                }
            } else {
                console.warn(`Link não encontrado: ${linkId}`);
            }
        });

    } catch (err) {
        console.error('Erro verificando permissões:', err);
    }
});

// Função local para verificar acesso
function verificarAcessoLocal(cargo, pagina) {
    const permissoes = {
        'administrador': {
            'cadastro_aluno': true,
            'ocorrencias': true,
            'relatorios': true,
            'historico': true,
            'criar_usuario': true,
            'gerenciar_usuarios': true
        },
        'coordenador': {
            'cadastro_aluno': false,
            'ocorrencias': false, 
            'relatorios': true,
            'historico': true,
            'criar_usuario': false,
            'gerenciar_usuarios': false
        },
        'analista': {
            'cadastro_aluno': true,
            'ocorrencias': true,
            'relatorios': false,
            'historico': true,
            'criar_usuario': false,
            'gerenciar_usuarios': false
        }
    };
    
    // Verifica se o cargo existe e se a página tem permissão definida
    if (permissoes[cargo] && permissoes[cargo].hasOwnProperty(pagina)) {
        return permissoes[cargo][pagina];
    }
    
    // Por segurança, nega acesso se não encontrar a permissão
    return false;
}

// Função de logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('cargo');
    alert('Você foi desconectado com sucesso.');
    window.location.href = 'index.html';
}