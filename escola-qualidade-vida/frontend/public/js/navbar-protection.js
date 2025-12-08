const API_BASE = "http://localhost:5000";

document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("access_token");
  const cargo = localStorage.getItem("cargo");

  if (!token || !cargo) {
    window.location.href = "index.html";
    return;
  }

  let perms = getPermissoesCache();
  if (!perms) perms = await carregarPermissoes();

  if (perms) {
    aplicarPermissoesNoNavbar(perms);
  }
});

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    ...(options.headers || {}),
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  let resp;
  try {
    resp = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch (err) {
    console.warn("⚠️ Erro de rede:", err);
    return { networkError: true };
  }

  if (resp.status === 401) {
    console.warn("🔒 Token expirado/inválido. Logout...");
    logout();
    return { unauthorized: true };
  }

  return resp;
}

function getPermissoesCache() {
  try {
    return JSON.parse(localStorage.getItem("user_permissions") || "null");
  } catch {
    return null;
  }
}

async function carregarPermissoes() {
  const resp = await apiFetch("/user_permissions", { method: "GET" });
  if (resp?.unauthorized || resp?.networkError) return null;

  if (resp.ok) {
    const data = await resp.json();
    localStorage.setItem("user_permissions", JSON.stringify(data.permissions));
    return data.permissions;
  }

  // erro 5xx etc: não derrube a UI
  console.warn("⚠️ Falha ao carregar permissões:", resp.status);
  return null;
}

function aplicarPermissoesNoNavbar(perms) {
  const links = [
    { selector: 'a[href="./cadastroAluno.html"]', pagina: "cadastro_aluno" },
    { selector: 'a[href="./consultaAluno.html"]', pagina: "consulta_aluno" },
    { selector: 'a[href="./importar_alunos.html"]', pagina: "importar_alunos" },
    { selector: 'a[href="./turmas.html"]', pagina: "cadastro_turma" },
    { selector: 'a[href="./ocorrencias.html"]', pagina: "ocorrencias" },
    { selector: 'a[href="./relatorios.html"]', pagina: "relatorios" },
    { selector: 'a[href="./dashboard.html"]', pagina: "dashboard" },
    { selector: 'a[href="./criar_usuario.html"]', pagina: "criar_usuario" },
  ];

  for (const { selector, pagina } of links) {
    document.querySelectorAll(selector).forEach((a) => {
      const ok = perms?.[pagina] === true;
      if (!ok) {
        a.removeAttribute("href");
        a.onclick = (e) => {
          e.preventDefault();
          alert("Você não tem permissão para acessar esta página!");
        };
        a.style.opacity = "0.5";
        a.style.cursor = "not-allowed";
      }
    });
  }
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_id");
  localStorage.removeItem("cargo");
  localStorage.removeItem("user_permissions");
  alert("Sua sessão expirou. Faça login novamente.");
  window.location.href = "index.html";
}
