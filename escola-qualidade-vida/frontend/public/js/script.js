document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  const cargo = localStorage.getItem("cargo");

  if (!token || !cargo) {
    window.location.href = "index.html";
    return;
  }

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);

  verificarPermissoesBackend();
  inicializarProtecaoLinks();
});

async function verificarPermissoesBackend() {
  try {
    const response = await fetch("/user_permissions", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem("user_permissions", JSON.stringify(data.permissions || {}));
    }
  } catch (error) {
    console.warn("Não foi possível atualizar as permissões do usuário.", error);
  }
}

async function inicializarProtecaoLinks() {
  const linksPorPermissao = {
    "link-cadastro-aluno": "cadastro_aluno",
    "link-ocorrencias": "ocorrencias",
    "link-relatorios": "relatorios",
    "link-dashboard": "dashboard",
    "link-criar-usuario": "criar_usuario",
    "link-importar-alunos": "importar_alunos",
    "link-cadastro-turma": "cadastro_turma",
    "link-consulta-aluno": "consulta_aluno",
  };

  Object.entries(linksPorPermissao).forEach(([linkId, pagina]) => {
    const link = document.getElementById(linkId);
    if (!link) return;

    const destino = link.href;
    link.addEventListener("click", async (event) => {
      event.preventDefault();
      const temAcesso = await verificarAcessoBackend(pagina);

      if (temAcesso) {
        window.location.href = destino;
        return;
      }

      alert("Seu perfil não tem acesso a esta página.");
    });
  });
}

async function verificarAcessoBackend(pagina) {
  try {
    const response = await fetch(`/check_permission/${pagina}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) return false;
    const data = await response.json();
    return data.has_permission === true;
  } catch {
    return false;
  }
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_id");
  localStorage.removeItem("cargo");
  localStorage.removeItem("user_permissions");
  window.location.href = "index.html";
}
