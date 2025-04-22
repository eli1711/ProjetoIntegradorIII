document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginAlert = document.getElementById('loginAlert');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    senha: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Login bem-sucedido
                loginAlert.textContent = 'Login realizado com sucesso! Redirecionando...';
                loginAlert.className = 'alert success';
                
                // Armazena o token JWT
                localStorage.setItem('authToken', data.access_token);
                
                // Redireciona após 2 segundos
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 2000);
            } else {
                // Exibe mensagem de erro
                loginAlert.textContent = data.detail || 'Erro ao realizar login';
                loginAlert.className = 'alert error';
            }
        } catch (error) {
            console.error('Erro:', error);
            loginAlert.textContent = 'Erro de conexão com o servidor';
            loginAlert.className = 'alert error';
        }
    });
    
    // Verifica se já está logado ao carregar a página
    checkAuthStatus();
});

function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // Se já estiver logado, redireciona para o dashboard
        window.location.href = 'dashboard.html';
    }
}