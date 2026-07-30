document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("userForm");
  const messageElement = document.getElementById("message");

  if (!form || !messageElement) return;

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const payload = {
      nome: document.getElementById("nome").value.trim(),
      email: document.getElementById("email").value.trim(),
      senha: document.getElementById("senha").value,
      cargo: document.getElementById("cargo").value,
    };

    renderMessage(messageElement, "Criando usuario...", "success");

    try {
      const response = await fetch("/api/criar_usuario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (response.ok && data.success) {
        renderMessage(messageElement, data.message || "Usuario criado com sucesso.", "success");
        form.reset();
        setTimeout(() => {
          window.location.href = "principal.html";
        }, 1200);
        return;
      }

      renderMessage(messageElement, data.message || "Falha ao criar usuario.", "error");
    } catch (error) {
      console.error("Erro na requisicao:", error);
      renderMessage(messageElement, "Erro de conexao. Verifique se o servidor esta rodando.", "error");
    }
  });
});

function renderMessage(target, message, type) {
  target.innerHTML = "";
  const div = document.createElement("div");
  div.className = type;
  div.textContent = message;
  target.appendChild(div);
}
