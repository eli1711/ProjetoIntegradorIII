(function () {
  const currentFile = (window.location.pathname.split("/").pop() || "index.html").toLowerCase();
  const isLogin = currentFile === "index.html" || currentFile === "redefinir_senha.html";
  const isHome = currentFile === "principal.html";

  const PAGE_META = {
    "cadastroaluno.html": {
      kicker: "Alunos",
      title: "Cadastro de aluno",
      subtitle: "Dados pessoais, responsavel, curso e turma vinculados ao cadastro escolar.",
      icon: "fa-user-plus",
    },
    "consultaaluno.html": {
      kicker: "Alunos",
      title: "Consulta de alunos",
      subtitle: "Pesquisa, revisao cadastral e atualizacao de informacoes do aluno.",
      icon: "fa-search",
    },
    "importar_alunos.html": {
      kicker: "Alunos",
      title: "Importacao CSV",
      subtitle: "Envio de planilhas e acompanhamento do processamento de alunos.",
      icon: "fa-file-csv",
    },
    "turmas.html": {
      kicker: "Academico",
      title: "Turmas",
      subtitle: "Cadastro, filtro por curso e controle de turmas ativas ou finalizadas.",
      icon: "fa-chalkboard",
    },
    "ocorrencias.html": {
      kicker: "Acompanhamento",
      title: "Ocorrencias",
      subtitle: "Registro de atendimentos, situacoes e encaminhamentos dos alunos.",
      icon: "fa-exclamation-triangle",
    },
    "ocorrencias_sensiveis.html": {
      kicker: "Acompanhamento",
      title: "Ocorrencias sensiveis",
      subtitle: "Monitoramento de acoes, prazos e status dos casos sensiveis.",
      icon: "fa-shield-heart",
    },
    "dashboard.html": {
      kicker: "Indicadores",
      title: "Dashboard",
      subtitle: "Indicadores consolidados de alunos, turmas, cursos e ocorrencias.",
      icon: "fa-chart-line",
    },
    "ia.html": {
      kicker: "Inteligencia de apoio",
      title: "IA de acompanhamento",
      subtitle: "Analise dados dos alunos e receba sugestoes praticas de acompanhamento escolar.",
      icon: "fa-wand-magic-sparkles",
    },
    "relatorios.html": {
      kicker: "Relatorios",
      title: "Relatorios de ocorrencias",
      subtitle: "Consulta analitica por aluno, curso, turma e tipo de ocorrencia.",
      icon: "fa-table",
    },
    "criar_usuario.html": {
      kicker: "Administracao",
      title: "Usuarios",
      subtitle: "Criacao de acessos para perfis administrativos e operacionais.",
      icon: "fa-user-cog",
    },
  };

  document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add(isLogin ? "ux-login" : "ux-app");
    if (isHome) document.body.classList.add("ux-home");
    document.body.dataset.page = currentFile.replace(".html", "");

    installSkipLink();
    markMainContent();
    enhanceNavigation();
    enhanceLogout();
    enhanceForms();
    enhanceTables();
    enhanceAlerts();
    setUserRole();
    installPageBanner();
    enhanceHomeMetrics();

    requestAnimationFrame(() => document.body.classList.add("ux-page-ready"));
  });

  function installSkipLink() {
    if (document.querySelector(".ux-skip-link")) return;

    const skip = document.createElement("a");
    skip.href = "#conteudo-principal";
    skip.className = "ux-skip-link";
    skip.textContent = "Ir para o conteudo";
    document.body.prepend(skip);
  }

  function markMainContent() {
    const main = document.querySelector("main, .container");
    if (main && !main.id) main.id = "conteudo-principal";
  }

  function enhanceNavigation() {
    const navMenu = document.getElementById("navMenu");
    const navToggle = document.getElementById("navToggle");
    if (!navMenu) return;

    ensureSensitiveOccurrencesNavLink(navMenu);
    ensureAiNavLink(navMenu);

    navMenu.querySelectorAll("a").forEach((link) => {
      const href = normalizeFile(link.getAttribute("href"));
      link.classList.remove("active");
      link.removeAttribute("aria-current");

      if (href === currentFile || (isHome && href === "principal.html")) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      }
    });

    const backdrop = ensureNavBackdrop();

    if (navToggle) {
      navToggle.setAttribute("aria-label", "Abrir menu");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.addEventListener("click", () => {
        const isOpen = navMenu.classList.toggle("show");
        navToggle.setAttribute("aria-expanded", String(isOpen));
        backdrop.classList.toggle("is-open", isOpen);
      });
    }

    backdrop.addEventListener("click", closeMobileMenu);

    navMenu.querySelectorAll("a[href]").forEach((link) => {
      link.addEventListener("click", () => {
        const href = link.getAttribute("href") || "";
        if (!href.startsWith("#")) closeMobileMenu();
      });
    });

    document.querySelectorAll(".dropdown > a").forEach((trigger) => {
      trigger.addEventListener("click", (event) => {
        if (window.matchMedia("(max-width: 980px)").matches) {
          event.preventDefault();
          trigger.parentElement.classList.toggle("open");
        }
      });
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMobileMenu();
    });

    window.addEventListener("resize", () => {
      if (!window.matchMedia("(max-width: 980px)").matches) closeMobileMenu();
    });
  }

  function ensureAiNavLink(navMenu) {
    if (navMenu.querySelector('a[href="./ia.html"], a[href="ia.html"]')) return;

    const usuariosLink = navMenu.querySelector('a[href="./criar_usuario.html"], a[href="criar_usuario.html"]');
    const item = document.createElement("li");
    item.innerHTML = '<a href="./ia.html"><i class="fas fa-wand-magic-sparkles"></i> IA</a>';

    if (usuariosLink?.parentElement) {
      navMenu.insertBefore(item, usuariosLink.parentElement);
    } else {
      navMenu.appendChild(item);
    }
  }

  function ensureSensitiveOccurrencesNavLink(navMenu) {
    if (navMenu.querySelector('a[href="./ocorrencias_sensiveis.html"], a[href="ocorrencias_sensiveis.html"]')) return;

    const dashboardLink = navMenu.querySelector('a[href="./dashboard.html"], a[href="dashboard.html"]');
    const item = document.createElement("li");
    item.innerHTML = '<a href="./ocorrencias_sensiveis.html"><i class="fas fa-shield-heart"></i> Sensiveis</a>';

    if (dashboardLink?.parentElement) {
      navMenu.insertBefore(item, dashboardLink.parentElement);
    } else {
      navMenu.appendChild(item);
    }
  }

  function ensureNavBackdrop() {
    let backdrop = document.querySelector(".ux-nav-backdrop");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.className = "ux-nav-backdrop";
      document.body.appendChild(backdrop);
    }
    return backdrop;
  }

  function closeMobileMenu() {
    const navMenu = document.getElementById("navMenu");
    const navToggle = document.getElementById("navToggle");
    const backdrop = document.querySelector(".ux-nav-backdrop");

    navMenu?.classList.remove("show");
    navToggle?.setAttribute("aria-expanded", "false");
    backdrop?.classList.remove("is-open");
    document.querySelectorAll(".dropdown.open").forEach((item) => item.classList.remove("open"));
  }

  function normalizeFile(href) {
    const raw = String(href || "").split("?")[0].split("#")[0];
    if (!raw || raw === "#") return "";
    return raw.split("/").pop().toLowerCase();
  }

  function enhanceLogout() {
    if (isLogin) return;

    const headerContent = document.querySelector(".header-content");
    if (!headerContent) return;

    let logoutButton = document.getElementById("logoutBtn") || document.getElementById("uxLogoutBtn");
    if (!logoutButton) {
      logoutButton = document.createElement("button");
      logoutButton.id = "uxLogoutBtn";
      logoutButton.type = "button";
      logoutButton.className = "ux-logout-btn";
      logoutButton.innerHTML = '<i class="fas fa-right-from-bracket" aria-hidden="true"></i><span>Sair</span>';
      headerContent.appendChild(logoutButton);
    } else {
      logoutButton.classList.add("ux-logout-btn");
      logoutButton.setAttribute("aria-label", "Sair");
    }

    if (logoutButton.dataset.uxLogoutBound === "true") return;
    logoutButton.dataset.uxLogoutBound = "true";

    logoutButton.addEventListener("click", () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_id");
      localStorage.removeItem("cargo");
      window.location.href = "index.html";
    });
  }

  function installPageBanner() {
    if (isLogin || isHome || document.querySelector(".ux-page-banner")) return;

    const meta = PAGE_META[currentFile];
    const main = document.querySelector("main, .container");
    if (!meta || !main) return;

    const banner = document.createElement("section");
    banner.className = "ux-page-banner";
    banner.innerHTML = `
      <div>
        <p class="ux-page-kicker">${meta.kicker}</p>
        <h1 class="ux-page-title"><i class="fas ${meta.icon}" aria-hidden="true"></i> ${meta.title}</h1>
        <p class="ux-page-subtitle">${meta.subtitle}</p>
      </div>
      <div class="ux-page-meta">
        <i class="fas fa-user-shield" aria-hidden="true"></i>
        <span id="uxPageRole">Perfil: ${formatRole(localStorage.getItem("cargo"))}</span>
      </div>
    `;

    main.prepend(banner);
  }

  function enhanceForms() {
    document.querySelectorAll("input[required], select[required], textarea[required]").forEach((field) => {
      const label = field.id ? document.querySelector(`label[for="${escapeAttribute(field.id)}"]`) : null;
      if (label && !label.dataset.requiredEnhanced && !label.textContent.includes("*")) {
        label.dataset.requiredEnhanced = "true";
        const marker = document.createElement("span");
        marker.setAttribute("aria-hidden", "true");
        marker.style.color = "var(--ux-brand)";
        marker.textContent = " *";
        label.appendChild(marker);
      }
    });

    document.querySelectorAll("input, select, textarea").forEach((field) => {
      const sync = () => field.classList.toggle("ux-has-value", Boolean(String(field.value || "").trim()));
      field.addEventListener("input", sync);
      field.addEventListener("change", sync);
      sync();
    });
  }

  function escapeAttribute(value) {
    return String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  }

  function enhanceTables() {
    document.querySelectorAll("table").forEach((table) => {
      table.classList.add("ux-responsive-table");

      const wrapper = table.parentElement;
      const alreadyWrapped = wrapper?.classList.contains("table-container") || wrapper?.classList.contains("ux-table-wrap");
      if (!alreadyWrapped && !wrapper?.style?.overflowX) {
        const wrap = document.createElement("div");
        wrap.className = "ux-table-wrap";
        table.parentNode.insertBefore(wrap, table);
        wrap.appendChild(table);
      }

      applyTableLabels(table);

      const tbody = table.querySelector("tbody");
      if (tbody && !table.dataset.uxTableObserved) {
        table.dataset.uxTableObserved = "true";
        new MutationObserver(() => applyTableLabels(table)).observe(tbody, { childList: true, subtree: true });
      }
    });
  }

  function applyTableLabels(table) {
    const headings = Array.from(table.querySelectorAll("thead th")).map((th) => th.textContent.trim());
    table.querySelectorAll("tbody tr").forEach((row) => {
      Array.from(row.children).forEach((cell, index) => {
        if (!cell.dataset.label && headings[index]) cell.dataset.label = headings[index];
      });
    });
  }

  function enhanceAlerts() {
    document.querySelectorAll("#alerta, .alert, .alerta, .message").forEach((alert) => {
      if (!alert.hasAttribute("role")) alert.setAttribute("role", "status");
      alert.setAttribute("aria-live", "polite");
    });
  }

  function setUserRole() {
    const role = formatRole(localStorage.getItem("cargo"));
    const targets = [
      document.getElementById("userRoleLabel"),
      document.getElementById("uxPageRole"),
    ].filter(Boolean);

    targets.forEach((target) => {
      if (target.id === "uxPageRole") {
        target.textContent = `Perfil: ${role}`;
      } else {
        target.textContent = role;
      }
    });
  }

  function formatRole(role) {
    const normalized = String(role || "usuario").trim().toLowerCase();
    const labels = {
      administrador: "Administrador",
      coordenador: "Coordenador",
      analista: "Analista",
      usuario: "Usuario",
    };
    return labels[normalized] || normalized.charAt(0).toUpperCase() + normalized.slice(1);
  }

  function enhanceHomeMetrics() {
    if (!isHome || document.querySelector(".ux-home-metrics")) return;

    const hero = document.querySelector(".workspace-hero");
    if (!hero) return;

    const metrics = document.createElement("section");
    metrics.className = "ux-home-metrics";
    metrics.setAttribute("aria-label", "Resumo do sistema");
    metrics.innerHTML = `
      <article class="ux-home-metric"><strong id="uxMetricAlunos">-</strong><span>Alunos</span></article>
      <article class="ux-home-metric"><strong id="uxMetricTurmas">-</strong><span>Turmas ativas</span></article>
      <article class="ux-home-metric"><strong id="uxMetricOcorrencias">-</strong><span>Ocorrencias</span></article>
    `;
    hero.insertAdjacentElement("afterend", metrics);

    if (!localStorage.getItem("access_token")) return;

    fetch("/dashboard?statusTurma=todas&limit=1", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => {
        if (!data) return;
        setText("uxMetricAlunos", data.totalAlunos);
        setText("uxMetricTurmas", data.turmasAtivas);
        setText("uxMetricOcorrencias", data.totalOcorrencias);
      })
      .catch(() => {
        setText("uxMetricAlunos", "-");
        setText("uxMetricTurmas", "-");
        setText("uxMetricOcorrencias", "-");
      });
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = value === undefined || value === null ? "-" : String(value);
  }
})();
