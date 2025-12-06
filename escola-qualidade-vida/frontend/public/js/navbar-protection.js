// desenvolvido por mim

document.addEventListener("DOMContentLoaded", function () {
  console.log("🔐 Iniciando proteção do navbar...");

  const token = localStorage.getItem("access_token");
  if (!token) return;

  protegerNavbar();
});

async function protegerNavbar() {
  try {
    console.log("🛡️ Protegendo links do navbar...");

    const linksParaProteger = [
      { href: "./cadastroAluno.html", pagina: "cadastro_aluno" },
      { href: "./consultaAluno.html", pagina: "consulta_aluno" },
      { href: "./importar_alunos.html", pagina: "importar_alunos" },
      { href: "./turmas.html", pagina: "cadastro_turma" },
      { href: "./ocorrencias.html", pagina: "ocorrencias" },
      { href: "./relatorios.html", pagina: "relatorios" },
      { href: "./dashboard.html", pagina: "dashboard" },
      { href: "./criar_usuario.html", pagina: "criar_usuario" },
    ];

    for (const linkInfo of linksParaProteger) {
      await verificarEProtegerLink(linkInfo.href, linkInfo.pagina);
    }
  } catch (error) {
    console.error("❌ Erro ao proteger navbar:", error);
  }
}

async function verificarEProtegerLink(href, pagina) {
  const links = document.querySelectorAll(`a[href="${href}"]`);

  if (links.length === 0) return;

  const temAcesso = await verificarPermissaoBackend(pagina);

  links.forEach((link) => {
    if (!temAcesso) {
      link.removeAttribute("href");
      link.onclick = function (e) {
        e.preventDefault();
        alert("Você não tem permissão para acessar esta página!");
        return false;
      };
    }
  });
}

async function verificarPermissaoBackend(pagina) {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return false;

    const response = await fetch(
      `http://localhost:5000/check_permission/${pagina}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (response.ok) {
      const data = await response.json();
      return data.has_permission;
    }
    return false;
  } catch (error) {
    console.error(`❌ Erro ao verificar permissão para ${pagina}:`, error);
    return false;
  }
}
