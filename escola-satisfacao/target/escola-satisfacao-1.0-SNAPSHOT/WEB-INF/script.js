document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `email=${encodeURIComponent(email)}&senha=${encodeURIComponent(senha)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            alert('Login realizado com sucesso!');
            // Redirecionar para a página de avaliação
            window.location.href = '/avaliacao.html'; // Exemplo de redirecionamento
        } else {
            alert('Email ou senha incorretos!');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
});