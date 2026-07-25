const API_BASE = window.API_BASE_URL || "";

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

function apiPath(path) {
  if (typeof window.apiUrl === "function") return window.apiUrl(path);
  return `${API_BASE}${path}`;
}

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = {
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  let resp;
  try {
    resp = await fetch(apiPath(path), { ...options, headers });
  } catch (err) {
    console.warn("Erro de rede:", err);
    return { networkError: true };
  }

  if (resp.status === 401) {
    console.warn("Token expirado/invalido. Logout...");
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

  console.warn("Falha ao carregar permissoes:", resp.status);
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
          alert("Voce nao tem permissao para acessar esta pagina!");
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
  alert("Sua sessao expirou. Faca login novamente.");
  window.location.href = "index.html";
}
