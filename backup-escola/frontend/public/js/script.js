document.addEventListener('DOMContentLoaded', function () {

    const logoutBtn = document.getElementById('logoutBtn');

    // ------------------- CHECA LOGIN E CARGO -------------------
    const token = localStorage.getItem('access_token');
    const cargo = localStorage.getItem('cargo');

    if (!token || !cargo) {
        // Usuário não logado, redireciona para login
        window.location.href = 'index.html';
        return;
    }

    // ------------------- LOGOUT -------------------
    logoutBtn && logoutBtn.addEventListener('click', logout);

    // ------------------- MAPA DE LINKS -------------------
    // IDs dos botões ou links na página principal
    const mapeamento_links = {
        'link-cadastro-aluno': 'cadastro_aluno',
        'link-ocorrencias': 'ocorrencias', 
        'link-relatorios': 'relatorios',
        'link-historico': 'historico',
        'link-criar-usuario': 'criar_usuario',
        
    };

    // ------------------- BLOQUEIO DE LINKS POR CARGO -------------------
    Object.keys(mapeamento_links).forEach(linkId => {
        const link = document.getElementById(linkId);
        if (link) {
            const pagina = mapeamento_links[linkId];
            const temAcesso = verificarAcessoLocal(cargo, pagina);

            if (!temAcesso) {
                // Bloqueia clique e avisa o usuário
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    alert('Você não tem permissão para acessar esta página!');
                });
            }
        }
    });
});

// ------------------- FUNÇÃO DE VERIFICAÇÃO DE PERMISSÕES -------------------
function verificarAcessoLocal(cargo, pagina) {
    const permissoes = {
        'administrador': {
            'cadastro_aluno': true,
            'ocorrencias': true,
            'relatorios': true,
            'historico': true,
            'criar_usuario': true,
            
        },
        'coordenador': {
            'cadastro_aluno': false,
            'ocorrencias': true, 
            'relatorios': true,
            'historico': true,
            'criar_usuario': false,
            
        },
        'analista': {
            'cadastro_aluno': true,
            'ocorrencias': true,
            'relatorios': false,
            'historico': true,
            'criar_usuario': false,
            
        }
    };
    
    if (permissoes[cargo] && permissoes[cargo].hasOwnProperty(pagina)) {
        return permissoes[cargo][pagina];
    }
    
    // Por segurança, nega acesso se não encontrar a permissão
    return false;
}

// ------------------- FUNÇÃO DE LOGOUT -------------------
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('cargo');
    alert('Você foi desconectado com sucesso.');
    window.location.href = 'index.html';
}
