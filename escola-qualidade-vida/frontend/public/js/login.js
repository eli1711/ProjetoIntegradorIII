document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const loginData = {
        username: document.getElementById('email').value,
        password: document.getElementById('senha').value
    };

    const response = await fetch('/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            'username': loginData.username,
            'password': loginData.password
        })
    });

    const result = await response.json();

    if (response.ok) {
        localStorage.setItem('access_token', result.access_token); // Armazenando o token JWT
        alert('Login bem-sucedido!');
        window.location.href = "/principal.html"; // Redireciona após login
    } else {
        alert(`Erro: ${result.detail}`);
    }
});
