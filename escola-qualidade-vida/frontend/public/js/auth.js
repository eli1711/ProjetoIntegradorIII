document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    const alertBox = document.getElementById('loginAlert');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const senha = document.getElementById('password').value.trim();

        const API_URL = "/auth"; // Prefixo da rota da API Flask (ajustada pelo Nginx)

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, senha })
            });

            const result = await response.json();

            if (response.ok && result.token) {
                // Armazena o token JWT
                localStorage.setItem('token', result.token);

                // Redireciona para a página principal
                window.location.href = "http://localhost/principal.html";

            } else {
                showAlert(result.erro || result.mensagem || "Falha no login");
            }
        } catch (error) {
            console.error("Erro ao fazer login:", error);
            showAlert("Erro de conexão com o servidor.");
        }
    });

    function showAlert(message) {
        alertBox.className = 'alert error';
        alertBox.innerText = message;
        alertBox.style.display = 'block';
    }
});
