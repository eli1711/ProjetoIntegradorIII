document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById("userForm");
    
    if (form) {
        form.addEventListener("submit", function(event) {
            event.preventDefault();

            const nome = document.getElementById("nome").value;
            const email = document.getElementById("email").value;
            const senha = document.getElementById("senha").value;
            const cargo = document.getElementById("cargo").value;

            console.log('Enviando dados para criação de usuário:', { nome, email, cargo });

            // Mostrar loading
            const messageElement = document.getElementById('message');
            messageElement.innerHTML = '<div class="success">Criando usuário...</div>';

            fetch('http://localhost:5000/api/criar_usuario', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    nome: nome,
                    email: email,
                    senha: senha,
                    cargo: cargo
                })
            })
            .then(response => {
                console.log('Status da resposta:', response.status);
                return response.json().then(data => {
                    return { status: response.status, data: data };
                });
            })
            .then(({ status, data }) => {
                console.log('Resposta completa:', { status, data });
                
                const messageElement = document.getElementById('message');
                if (data.success) {
                    messageElement.innerHTML = `<div class="success">✅ ${data.message}</div>`;
                    form.reset();
                    
                    // Redirecionar após 2 segundos
                    setTimeout(() => {
                        window.location.href = 'principal.html';
                    }, 2000);
                } else {
                    messageElement.innerHTML = `<div class="error">❌ ${data.message}</div>`;
                }
            })
            .catch(error => {
                console.error('Erro na requisição:', error);
                const messageElement = document.getElementById('message');
                messageElement.innerHTML = `<div class="error">❌ Erro de conexão. Verifique se o servidor está rodando.</div>`;
            });
        });
    } else {
        console.error('Formulário não encontrado!');
    }
});