document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const loginAlert = document.getElementById('loginAlert');

    if (!loginForm || !loginAlert) {
        console.error("Formulário ou alerta de login não encontrado no DOM.");
        return;
    }

    loginForm.addEventListener('submit', function (event) {
        handleLogin(event, loginAlert);
    });

    checkAuthStatus();
});

async function handleLogin(event, loginAlert) {
    event.preventDefault();

    const emailInput = document.getElementById('email');
    const senhaInput = document.getElementById('password');

    if (!emailInput || !senhaInput) {
        exibirMensagem(loginAlert, "Erro: Campos de e-mail ou senha não encontrados.", "error");
        return;
    }

    const loginData = {
        email: emailInput.value.trim(),
        senha: senhaInput.value.trim()
    };

    if (!loginData.email || !loginData.senha) {
        exibirMensagem(loginAlert, "Por favor, preencha o e-mail e a senha.", "error");
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            exibirMensagem(loginAlert, "✅ Login bem-sucedido! Redirecionando...", "success");
            setTimeout(() => {
                window.location.href = 'principal.html';
            }, 1500); // Delay para a mensagem de sucesso aparecer
        } else {
            exibirMensagem(loginAlert, data.erro || "❌ E-mail ou senha inválidos.", "error");
        }
    } catch (err) {
        console.error("Erro na requisição de login:", err);
        exibirMensagem(loginAlert, "❌ Erro inesperado ao tentar fazer login.", "error");
    }
}

function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    if (token) {
        window.location.href = 'principal.html';
    }
}

// Função para exibir mensagens com estilo
function exibirMensagem(elemento, mensagem, tipo) {
    elemento.textContent = mensagem;
    elemento.classList.remove('success', 'error'); // Limpa estilos antigos
    elemento.classList.add(tipo); // Aplica nova classe de sucesso ou erro
    elemento.style.display = "block"; // Garante que a mensagem será exibida
}
