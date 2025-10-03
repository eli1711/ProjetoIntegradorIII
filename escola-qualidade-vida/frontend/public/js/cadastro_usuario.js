document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById("userForm");
    
    if (form) {
        form.addEventListener("submit", function(event) {
            event.preventDefault();

            const nome = document.getElementById("nome").value;
            const email = document.getElementById("email").value;
            const senha = document.getElementById("senha").value;
            const cargo = document.getElementById("cargo").value;

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
            .then(response => response.json())
            .then(data => {
                const messageElement = document.getElementById('message');
                if (data.success) {
                    messageElement.innerHTML = `<div class="success">${data.message}</div>`;
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
