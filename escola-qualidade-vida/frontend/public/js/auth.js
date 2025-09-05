document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const loginAlert = document.getElementById('loginAlert');

    // Verificar se já existe um token de autenticação
    if (localStorage.getItem('access_token')) {
        // Se o token existir, redireciona diretamente para a página principal
        window.location.href = 'principal.html';
        return;
    }

    if (!loginForm || !loginAlert) {
        console.error("Formulário ou alerta de login não encontrado no DOM.");
        return;
    }

    loginForm.addEventListener('submit', function (event) {
        handleLogin(event, loginAlert);
    });

    // Inicializar funcionalidade de recuperação de senha
    initPasswordRecovery();
});

// Função para inicializar a recuperação de senha
function initPasswordRecovery() {
    // Modal de recuperação de senha
    const modal = document.getElementById("forgotPasswordModal");
    const btn = document.querySelector(".forgot-password");
    const span = document.querySelector(".close");
    const recoveryForm = document.getElementById("forgotPasswordForm");

    // Verificar se os elementos existem antes de adicionar event listeners
    if (!modal || !btn || !span || !recoveryForm) {
        console.warn("Elementos de recuperação de senha não encontrados no DOM.");
        return;
    }

    btn.addEventListener('click', function(e) {
        e.preventDefault();
        modal.style.display = "block";
    });

    span.addEventListener('click', function() {
        modal.style.display = "none";
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Formulário de recuperação
    recoveryForm.addEventListener("submit", function(e) {
        e.preventDefault();
        
        const emailInput = document.getElementById("recoveryEmail");
        const messageElement = document.getElementById("recoveryMessage");
        
        if (!emailInput || !messageElement) {
            console.error("Elementos de recuperação não encontrados");
            return;
        }
        
        const email = emailInput.value.trim();
        
        if (!email) {
            messageElement.innerHTML = '<div class="error">Por favor, informe o e-mail</div>';
            return;
        }
        
        // URL CORRIGIDA - use a mesma base do login
        fetch('http://localhost:5000/auth/recuperar_senha', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                messageElement.innerHTML = `<div class="success">${data.message}</div>`;
                // Limpar formulário após sucesso
                recoveryForm.reset();
                
                // Fechar modal após 3 segundos
                setTimeout(() => {
                    modal.style.display = "none";
                    messageElement.innerHTML = ''; // Limpar mensagem
                }, 3000);
            } else {
                messageElement.innerHTML = `<div class="error">${data.message}</div>`;
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            messageElement.innerHTML = '<div class="error">Erro ao processar solicitação. Tente novamente.</div>';
        });
    });
}

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

        // Verifica se a resposta é OK antes de tentar parsear JSON
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erro HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();

        if (data.access_token) {
            // Armazena o token no localStorage
            localStorage.setItem('access_token', data.access_token);
            exibirMensagem(loginAlert, "✅ Login bem-sucedido! Redirecionando...", "success");
            setTimeout(() => {
                window.location.href = 'principal.html';
            }, 1500);
        } else {
            exibirMensagem(loginAlert, data.erro || data.message || "❌ E-mail ou senha inválidos.", "error");
        }
    } catch (err) {
        console.error("Erro na requisição de login:", err);
        exibirMensagem(loginAlert, "❌ Erro inesperado ao tentar fazer login.", "error");
    }
}

// Função para exibir mensagens com estilo
function exibirMensagem(elemento, mensagem, tipo) {
    if (!elemento) {
        console.error("Elemento para exibir mensagem não encontrado");
        return;
    }
    
    elemento.innerHTML = ''; // Limpar conteúdo anterior
    const messageDiv = document.createElement('div');
    messageDiv.textContent = mensagem;
    messageDiv.className = tipo;
    elemento.appendChild(messageDiv);
    elemento.style.display = "block";
    
    // Auto-esconder mensagens de erro após 5 segundos
    if (tipo === 'error') {
        setTimeout(() => {
            elemento.style.display = "none";
            elemento.innerHTML = '';
        }, 5000);
    }
}