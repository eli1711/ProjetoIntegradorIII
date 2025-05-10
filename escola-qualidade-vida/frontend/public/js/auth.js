document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const loginAlert = document.getElementById('loginAlert');
    
    loginForm.addEventListener('submit', handleLogin);
    
    // Verifica o estado de autenticação ao carregar a página
    checkAuthStatus();
});

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const loginAlert = document.getElementById('loginAlert');

    // Valida os campos de entrada
    if (!email || !password) {
        displayAlert('E-mail e senha são obrigatórios', 'error');
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, senha: password })
        });

        const data = await response.json();

        if (response.ok) {
            // Login bem-sucedido
            displayAlert('Login realizado com sucesso! Redirecionando...', 'success');
            localStorage.setItem('authToken', data.token);  // Salva o token JWT
            setTimeout(() => window.location.href = 'principal.html', 2000);
        } else {
            // Exibe mensagem de erro
            displayAlert(data.detail || 'Erro ao realizar login', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        displayAlert('Erro de conexão com o servidor', 'error');
    }
}

function displayAlert(message, type) {
    const loginAlert = document.getElementById('loginAlert');
    loginAlert.textContent = message;
    loginAlert.className = `alert ${type}`; // 'alert success' ou 'alert error'
}

function checkAuthStatus() {
    const token = localStorage.getItem('authToken');

    // Se o token existir e for válido, redireciona para o dashboard
    if (token) {
        if (isTokenValid(token)) {
            window.location.href = 'principal.html';
        } else {
            localStorage.removeItem('authToken'); // Remove o token expirado
            console.log('Token expirado, redirecionando para login...');
        }
    } else {
        // Se o token não estiver presente, mantém na página de login
        console.log('Token não encontrado, permanecendo na página de login...');
    }
}

function isTokenValid(token) {
    try {
        // Tenta decodificar o token
        const decoded = jwt.decode(token);
        const currentTime = Math.floor(Date.now() / 1000);

        // Verifica se o token expirou
        if (decoded.exp < currentTime) {
            localStorage.removeItem('authToken'); // Remove o token expirado
            return false;
        }
        return true;
    } catch (e) {
        console.error('Token inválido:', e);
        localStorage.removeItem('authToken'); // Remove o token inválido
        return false;
    }
}
