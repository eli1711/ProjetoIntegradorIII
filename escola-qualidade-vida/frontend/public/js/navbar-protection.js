(() => {
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
      if (!garantirPermissaoDaPagina(perms)) return;
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

    try {
      const resp = await fetch(apiPath(path), { ...options, headers });
      if (resp.status === 401) {
        logout();
        return { unauthorized: true };
      }
      return resp;
    } catch {
      return { networkError: true };
    }
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
      localStorage.setItem("user_permissions", JSON.stringify(data.permissions || {}));
      return data.permissions || {};
    }

    return null;
  }

  function aplicarPermissoesNoNavbar(perms) {
    const links = [
      { selector: 'a[href="./cadastroAluno.html"]', pagina: "cadastro_aluno" },
      { selector: 'a[href="./consultaAluno.html"]', pagina: "consulta_aluno" },
      { selector: 'a[href="./importar_alunos.html"]', pagina: "importar_alunos" },
      { selector: 'a[href="./turmas.html"]', pagina: "cadastro_turma" },
      { selector: 'a[href="./ocorrencias.html"]', pagina: "ocorrencias" },
      { selector: 'a[href="./ocorrencias_sensiveis.html"]', pagina: "ocorrencias" },
      { selector: 'a[href="./relatorios.html"]', pagina: "relatorios" },
      { selector: 'a[href="./dashboard.html"]', pagina: "dashboard" },
      { selector: 'a[href="./ia.html"]', pagina: "dashboard" },
      { selector: 'a[href="./criar_usuario.html"]', pagina: "criar_usuario" },
    ];

    for (const { selector, pagina } of links) {
      document.querySelectorAll(selector).forEach((link) => {
        if (perms?.[pagina] === true) return;

        link.removeAttribute("href");
        link.setAttribute("aria-disabled", "true");
        link.classList.add("is-disabled");
        link.addEventListener("click", (event) => {
          event.preventDefault();
          alert("Seu perfil não tem acesso a esta página.");
        });
      });
    }
  }

  function garantirPermissaoDaPagina(perms) {
    const currentFile = (window.location.pathname.split("/").pop() || "principal.html").toLowerCase();
    const permissoesPorPagina = {
      "cadastroaluno.html": "cadastro_aluno",
      "consultaaluno.html": "consulta_aluno",
      "importar_alunos.html": "importar_alunos",
      "turmas.html": "cadastro_turma",
      "ocorrencias.html": "ocorrencias",
      "ocorrencias_sensiveis.html": "ocorrencias",
      "relatorios.html": "relatorios",
      "dashboard.html": "dashboard",
      "ia.html": "dashboard",
      "criar_usuario.html": "criar_usuario",
    };

    const permissao = permissoesPorPagina[currentFile];
    if (!permissao || perms?.[permissao] === true) return true;

    alert("Seu perfil não tem acesso a esta página.");
    window.location.href = "principal.html";
    return false;
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("cargo");
    localStorage.removeItem("user_permissions");
    alert("Sua sessão expirou. Faça login novamente.");
    window.location.href = "index.html";
  }
})();
