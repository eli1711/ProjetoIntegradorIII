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
        'link-importar-alunos': 'importar_alunos',
        'link-cadastro-turma': 'cadastro_turma',
        'link-consulta-aluno': 'consulta_aluno'
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
            'importar_alunos': true,
            'cadastro_turma': true,
            'consulta_aluno': true

        },
        'coordenador': {
            'cadastro_aluno': false,
            'ocorrencias': true, 
            'relatorios': true,
            'historico': true,
            'criar_usuario': false,
            'importar_alunos': true,
            'cadastro_turma': false,
            'consulta_aluno': true, 
        },
        'analista': {
            'cadastro_aluno': true,
            'ocorrencias': true,
            'relatorios': false,
            'historico': true,
            'criar_usuario': false,
            'importar_alunos':false,
            'cadastro_turma':true,
            'consulta_aluno':true,
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


 document.addEventListener('DOMContentLoaded', function () {
            const logoutBtn = document.getElementById('logoutBtn');

            // ------------------- CHECA LOGIN E CARGO -------------------
            const token = localStorage.getItem('access_token');
            const cargo = localStorage.getItem('cargo');

            if (!token || !cargo) {
                window.location.href = 'index.html';
                return;
            }

            // ------------------- LOGOUT -------------------
            if (logoutBtn) {
                logoutBtn.addEventListener('click', logout);
            }

            // ------------------- MAPA DE LINKS -------------------
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
                        link.addEventListener('click', function(e) {
                            e.preventDefault();
                            alert('Você não tem permissão para acessar esta página!');
                        });
                    }
                }
            });
        });

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
            
            return permissoes[cargo] && permissoes[cargo][pagina] === true;
        }
