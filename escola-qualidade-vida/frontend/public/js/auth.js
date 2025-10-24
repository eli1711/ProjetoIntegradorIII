document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const loginAlert = document.getElementById('loginAlert');

    // Verificar se já existe um token de autenticação
    if (localStorage.getItem('access_token')) {
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
    
    // Testar conexão com o backend
    testBackendConnection();
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
        
        // @ts-ignore
        const email = emailInput.value.trim();
        
        if (!email) {
            messageElement.innerHTML = '<div class="error">Por favor, informe o e-mail</div>';
            return;
        }
        
        console.log('📤 Enviando requisição para recuperação de senha...');
        console.log('📧 Email:', email);
        
        // Primeiro teste com a rota simplificada
        testRecoveryRoute().then(() => {
            // Se a rota de teste funcionar, então envia para a rota real
            sendRecoveryRequest(email, modal, messageElement, recoveryForm);
        }).catch(error => {
            console.error('❌ Rota de teste falhou:', error);
            messageElement.innerHTML = '<div class="error">Servidor indisponível. Tente novamente mais tarde.</div>';
        });
    });
}

// Função para testar a rota de recuperação
async function testRecoveryRoute() {
    try {
        const response = await fetch('http://localhost:5000/auth/recuperar_senha_test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: 'test@example.com' })
        });
        
        if (!response.ok) {
            throw new Error('Erro na rota de teste: ' + response.status);
        }
        
        const data = await response.json();
        console.log('✅ Rota de teste funcionando:', data);
        return data;
    } catch (error) {
        console.error('❌ Erro na rota de teste:', error);
        throw error;
    }
}

// Função para enviar a requisição real
async function sendRecoveryRequest(email, modal, messageElement, recoveryForm) {
    try {
        const response = await fetch('http://localhost:5000/auth/recuperar_senha', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        console.log('📥 Resposta recebida:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erro ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('📊 Dados recebidos:', data);
        
        if (data.success) {
            // ALERTA DE E-MAIL ENCONTRADO E ENVIADO
            messageElement.innerHTML = `<div class="success">✅ ${data.message || 'E-mail encontrado! Link de recuperação enviado com sucesso.'}</div>`;
            recoveryForm.reset();
            
            setTimeout(() => {
                modal.style.display = "none";
                messageElement.innerHTML = '';
            }, 3000);
        } else {
            // ALERTA DE E-MAIL NÃO ENCONTRADO
            messageElement.innerHTML = `<div class="error">❌ ${data.message || 'Este e-mail não está cadastrado em nosso sistema.'}</div>`;
        }
    } catch (error) {
        console.error('❌ Erro completo:', error);
        // ALERTA DE ERRO NO PROCESSAMENTO
        messageElement.innerHTML = '<div class="error">❌ Erro ao processar solicitação. Verifique o console para detalhes.</div>';
    }
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
        // @ts-ignore
        email: emailInput.value.trim(),
        // @ts-ignore
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

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erro HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();

        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('cargo', data.cargo);
            
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
    
    elemento.innerHTML = '';
    const messageDiv = document.createElement('div');
    messageDiv.textContent = mensagem;
    messageDiv.className = tipo;
    elemento.appendChild(messageDiv);
    elemento.style.display = "block";
    
    if (tipo === 'error') {
        setTimeout(() => {
            elemento.style.display = "none";
            elemento.innerHTML = '';
        }, 5000);
    }
}

// Função para testar a conexão com o backend
async function testBackendConnection() {
    try {
        const response = await fetch('http://localhost:5000/auth/test');
        const data = await response.json();
        console.log('✅ Teste de conexão com backend:', data);
    } catch (error) {
        console.error('❌ Erro na conexão com backend:', error);
    }
}