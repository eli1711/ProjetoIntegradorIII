// @ts-nocheck

// Aguarda o DOM carregar completamente
document.addEventListener('DOMContentLoaded', function() {
    // Função que será chamada quando o formulário for enviado
    const form = document.getElementById("userForm");
    
    if (form) {
        form.addEventListener("submit", function(event) {
            event.preventDefault(); // Impede o envio tradicional do formulário

            // Coleta os valores dos campos
            const nome = document.getElementById("nome").value;
            const email = document.getElementById("email").value;
            const senha = document.getElementById("senha").value;
            const cargo = document.getElementById("cargo").value;

            // Fazendo a requisição para o backend Flask
            fetch('http://localhost:5000/api/criar_usuario', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    nome: nome,
                    email: email,
                    senha: senha,
                    cargo: cargo // Campo cargo adicionado
                })
            })
            .then(response => response.json())
            .then(data => {
                // Exibe a mensagem de sucesso ou erro
                const messageElement = document.getElementById('message');
                if (data.success) {
                    messageElement.innerHTML = `<div class="success">${data.message}</div>`;
                    // Limpa o formulário após sucesso
                    form.reset();
                } else {
                    messageElement.innerHTML = `<div class="error">${data.message}</div>`;
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                const messageElement = document.getElementById('message');
                messageElement.innerHTML = `<div class="error">Erro ao criar o usuário, tente novamente!</div>`;
            });
        });
    } else {
        console.error('Formulário não encontrado!');
    }
});