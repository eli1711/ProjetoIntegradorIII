document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");
  const loginAlert = document.getElementById("loginAlert");

  if (localStorage.getItem("access_token")) {
    window.location.href = "principal.html";
    return;
  }

  if (!loginForm || !loginAlert) return;

  loginForm.addEventListener("submit", function (event) {
    handleLogin(event, loginAlert);
  });

  initPasswordRecovery();
});

function initPasswordRecovery() {
  const modal = document.getElementById("forgotPasswordModal");
  const btn = document.querySelector(".forgot-password");
  const closeBtn = document.querySelector(".close");
  const recoveryForm = document.getElementById("forgotPasswordForm");

  if (!modal || !btn || !closeBtn || !recoveryForm) return;

  btn.addEventListener("click", function (event) {
    event.preventDefault();
    modal.style.display = "block";
    modal.setAttribute("aria-hidden", "false");
  });

  closeBtn.addEventListener("click", closeForgotPasswordModal);
  window.addEventListener("click", function (event) {
    if (event.target === modal) closeForgotPasswordModal();
  });

  recoveryForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const emailInput = document.getElementById("recoveryEmail");
    const messageElement = document.getElementById("recoveryMessage");
    const email = (emailInput?.value || "").trim();

    if (!email) {
      renderMessage(messageElement, "Por favor, informe o e-mail.", "error");
      return;
    }

    try {
      const response = await fetch("/auth/recuperar_senha", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await response.json();

      if (!response.ok || !data.success) {
        renderMessage(messageElement, data.message || "Erro ao solicitar recuperacao.", "error");
        return;
      }

      renderMessage(messageElement, data.message, "success");
      recoveryForm.reset();
      setTimeout(closeForgotPasswordModal, 3000);
    } catch (error) {
      console.error("Erro na recuperacao de senha:", error);
      renderMessage(messageElement, "Servidor indisponivel. Tente novamente mais tarde.", "error");
    }
  });
}

async function handleLogin(event, loginAlert) {
  event.preventDefault();

  const emailInput = document.getElementById("email");
  const senhaInput = document.getElementById("password");
  const loginData = {
    email: (emailInput?.value || "").trim(),
    senha: (senhaInput?.value || "").trim(),
  };

  if (!loginData.email || !loginData.senha) {
    exibirMensagem(loginAlert, "Por favor, preencha o e-mail e a senha.", "error");
    return;
  }

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loginData),
    });
    const data = await response.json();

    if (response.ok && data.access_token) {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("cargo", data.cargo);

      exibirMensagem(loginAlert, "Login bem-sucedido. Redirecionando...", "success");
      setTimeout(() => {
        window.location.href = "principal.html";
      }, 800);
      return;
    }

    exibirMensagem(loginAlert, data.erro || data.message || "E-mail ou senha invalidos.", "error");
  } catch (error) {
    console.error("Erro na requisicao de login:", error);
    exibirMensagem(loginAlert, "Erro inesperado ao tentar fazer login.", "error");
  }
}

function renderMessage(elemento, mensagem, tipo) {
  if (!elemento) return;
  elemento.innerHTML = "";
  const div = document.createElement("div");
  div.className = tipo;
  div.textContent = mensagem;
  elemento.appendChild(div);
  elemento.style.display = "block";
}

function exibirMensagem(elemento, mensagem, tipo) {
  renderMessage(elemento, mensagem, tipo);
  if (tipo === "error") {
    setTimeout(() => {
      if (elemento) {
        elemento.style.display = "none";
        elemento.innerHTML = "";
      }
    }, 5000);
  }
}

function openForgotPasswordModal() {
  const modal = document.getElementById("forgotPasswordModal");
  if (!modal) return;
  modal.style.display = "block";
  modal.setAttribute("aria-hidden", "false");
}

function closeForgotPasswordModal() {
  const modal = document.getElementById("forgotPasswordModal");
  const messageElement = document.getElementById("recoveryMessage");
  if (modal) {
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
  }
  if (messageElement) messageElement.innerHTML = "";
}
