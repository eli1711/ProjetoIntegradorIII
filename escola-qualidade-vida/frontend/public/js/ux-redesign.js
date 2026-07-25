(function () {
  const currentFile = (window.location.pathname.split("/").pop() || "index.html").toLowerCase();
  const isLogin = currentFile === "index.html" || currentFile === "redefinir_senha.html";

  document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add(isLogin ? "ux-login" : "ux-app");
    if (currentFile === "principal.html") document.body.classList.add("ux-home");

    const skip = document.createElement("a");
    skip.href = "#conteudo-principal";
    skip.className = "ux-skip-link";
    skip.textContent = "Ir para o conteúdo";
    document.body.prepend(skip);

    const main = document.querySelector("main, .container");
    if (main && !main.id) main.id = "conteudo-principal";

    enhanceNavigation();
    enhanceLogout();
    enhanceForms();
    setUserRole();
  });

  function enhanceNavigation() {
    const navMenu = document.getElementById("navMenu");
    const navToggle = document.getElementById("navToggle");
    if (!navMenu) return;

    navMenu.querySelectorAll("a").forEach((link) => {
      const href = (link.getAttribute("href") || "").split("/").pop().toLowerCase();
      link.classList.remove("active");
      link.removeAttribute("aria-current");

      if (href === currentFile || (currentFile === "principal.html" && href === "principal.html")) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      }
    });

    if (navToggle) {
      navToggle.setAttribute("aria-label", "Abrir menu");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.addEventListener("click", () => {
        const isOpen = navMenu.classList.toggle("show");
        navToggle.setAttribute("aria-expanded", String(isOpen));
      });
    }

    document.querySelectorAll(".dropdown > a").forEach((trigger) => {
      trigger.addEventListener("click", (event) => {
        if (window.matchMedia("(max-width: 980px)").matches) {
          event.preventDefault();
          trigger.parentElement.classList.toggle("open");
        }
      });
    });
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
    }

    logoutButton.addEventListener("click", () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_id");
      localStorage.removeItem("cargo");
      window.location.href = "index.html";
    });
  }

  function enhanceForms() {
    document.querySelectorAll("input[required], select[required], textarea[required]").forEach((field) => {
      const label = document.querySelector(`label[for="${field.id}"]`);
      if (label && !label.dataset.requiredEnhanced && !label.textContent.includes("*")) {
        label.dataset.requiredEnhanced = "true";
        label.insertAdjacentHTML("beforeend", ' <span aria-hidden="true" style="color: var(--ux-brand)">*</span>');
      }
    });
  }

  function setUserRole() {
    const role = localStorage.getItem("cargo");
    const target = document.getElementById("userRoleLabel");
    if (!target || !role) return;
    target.textContent = role.charAt(0).toUpperCase() + role.slice(1);
  }
})();
