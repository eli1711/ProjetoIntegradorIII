document.addEventListener('DOMContentLoaded', function () {
    const logoutBtn = document.getElementById('logoutBtn');

    // Verifica se o usuário está logado
    if (!localStorage.getItem('access_token')) {
        // Se não houver token, redireciona para a página de login
        window.location.href = 'index.html';
    }

    // Adiciona a função de logout ao botão
    logoutBtn.addEventListener('click', logout);
});

// Função de logout
function logout() {
    // Remove o token JWT do localStorage
    localStorage.removeItem('access_token');

    // Exibe uma mensagem de logout
    alert('Você foi desconectado com sucesso.');

    // Redireciona para a página de login
    window.location.href = 'index.html';  // Redirecionamento para a página de login
}

document.addEventListener("DOMContentLoaded", async () => {
  const userId = localStorage.getItem("user_id"); // salvo no login
  const cargo = localStorage.getItem("cargo");

  if (cargo === "administrador") {
    const res = await fetch(`http://localhost:5000/usuarios/${userId}/permissoes`);
    const permissoes = await res.json();

    document.querySelectorAll("main .a").forEach(link => {
      const id = link.id;
      if (permissoes[id] === false) {
        link.style.display = "none"; // 🔒 oculta link bloqueado
      }
    });
  }
});
