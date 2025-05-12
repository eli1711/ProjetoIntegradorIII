document.addEventListener('DOMContentLoaded', function () {
    const logoutBtn = document.getElementById('logoutBtn');

    // Verifica se o usuário está logado
    if (!localStorage.getItem('access_token')) {
        // Se não houver token, redireciona para a página de login
        window.location.href = 'index.html';
    }

    // Adiciona a função de logout ao botão
    logoutBtn.addEventListener('click', logout);
});

// Função de logout
function logout() {
    // Remove o token JWT do localStorage
    localStorage.removeItem('access_token');

    // Exibe uma mensagem de logout
    alert('Você foi desconectado com sucesso.');

    // Redireciona para a página de login
    window.location.href = 'index.html';  // Redirecionamento para a página de login
}
