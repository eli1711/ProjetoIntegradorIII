document.addEventListener('DOMContentLoaded', function () {
    const logoutBtn = document.getElementById('logoutBtn');

    // ------------------- CHECA LOGIN E CARGO -------------------
    const token = localStorage.getItem('access_token');
    const cargo = localStorage.getItem('cargo');

    console.log('🔐 Token:', token ? 'Presente' : 'Ausente');
    console.log('👤 Cargo:', cargo);

    if (!token || !cargo) {
        console.log('❌ Usuário não logado, redirecionando...');
        window.location.href = 'index.html';
        return;
    }

    // ------------------- LOGOUT -------------------
    logoutBtn && logoutBtn.addEventListener('click', logout);

    // ------------------- VERIFICAÇÃO BACKEND DE PERMISSÕES -------------------
    verificarPermissoesBackend();

    // ------------------- BLOQUEIO DE LINKS BASEADO NO BACKEND -------------------
    inicializarProtecaoLinks();
});

// ------------------- FUNÇÃO DE VERIFICAÇÃO DE PERMISSÕES NO BACKEND -------------------
async function verificarPermissoesBackend() {
    try {
        console.log('🔄 Carregando permissões do backend...');
        
        const response = await fetch('http://localhost:5000/api/user_permissions', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        });

        console.log('📡 Resposta do backend:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Permissões carregadas:', data);
            localStorage.setItem('user_permissions', JSON.stringify(data.permissions));
        } else {
            const errorText = await response.text();
            console.error('❌ Erro ao carregar permissões:', errorText);
        }
    } catch (error) {
        console.error('❌ Erro na verificação de permissões:', error);
    }
}

// ------------------- INICIALIZAÇÃO DA PROTEÇÃO DE LINKS -------------------
async function inicializarProtecaoLinks() {
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

    console.log('🔗 Inicializando proteção de links...');

    for (const [linkId, pagina] of Object.entries(mapeamento_links)) {
        const link = document.getElementById(linkId);
        if (link) {
            console.log(`🔍 Configurando link: ${linkId} -> ${pagina}`);
            
            // Remove qualquer evento anterior
            const newLink = link.cloneNode(true);
            link.parentNode.replaceChild(newLink, link);
            
            newLink.addEventListener('click', async function(e) {
                e.preventDefault();
                console.log(`🖱️ Clicado no link: ${pagina}`);
                
                const temAcesso = await verificarAcessoBackend(pagina);
                console.log(`📊 Resultado do acesso para ${pagina}: ${temAcesso}`);
                
                if (temAcesso) {
                    console.log(`✅ Navegando para: ${newLink.href}`);
                    window.location.href = newLink.href;
                } else {
                    console.log(`❌ Acesso negado para: ${pagina}`);
                    alert('Você não tem permissão para acessar esta página!');
                }
            });
        } else {
            console.log(`⚠️ Link não encontrado: ${linkId}`);
        }
    }
}

// ------------------- VERIFICAÇÃO NO BACKEND -------------------
async function verificarAcessoBackend(pagina) {
    try {
        console.log(`🔐 Verificando acesso para: ${pagina}`);
        
        const response = await fetch(`http://localhost:5000/api/check_permission/${pagina}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                'Content-Type': 'application/json'
            }
        });

        console.log(`📡 Resposta do backend para ${pagina}:`, response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log(`📊 Dados de permissão:`, data);
            return data.has_permission;
        } else if (response.status === 403) {
            console.log(`🚫 Acesso explicitamente negado: ${pagina}`);
            return false;
        } else {
            const errorText = await response.text();
            console.error(`❌ Erro na verificação de permissão ${pagina}:`, response.status, errorText);
            return false;
        }
    } catch (error) {
        console.error(`❌ Erro ao verificar acesso para ${pagina}:`, error);
        return false;
    }
}

// ------------------- FUNÇÃO DE LOGOUT -------------------
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('cargo');
    localStorage.removeItem('user_permissions');
    alert('Você foi desconectado com sucesso.');
    window.location.href = 'index.html';
}