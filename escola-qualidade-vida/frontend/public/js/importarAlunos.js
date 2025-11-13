document.addEventListener("DOMContentLoaded", () => {
  const alertaDiv = document.getElementById('alerta');
  const btn = document.getElementById('btnImportar');
  const fileInput = document.getElementById('arquivo');
  const resultado = document.getElementById('resultado');
  const logEl = document.getElementById('log');
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  // Menu responsivo
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      navMenu.classList.toggle("show");
    });
  }

  function showAlert(tipo, msg) {
    alertaDiv.style.display = 'block';
    alertaDiv.className = (tipo === 'success') ? 'alert-success' : 'alert-error';
    alertaDiv.textContent = msg;
    setTimeout(() => alertaDiv.style.display = 'none', 7000);
  }

  btn.addEventListener('click', async () => {
    if (!fileInput.files.length) {
      showAlert('error', 'Selecione um arquivo CSV.');
      return;
    }
    const fd = new FormData();
    fd.append('arquivo', fileInput.files[0]);

    btn.disabled = true;
    const original = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Importando...';

    try {
      const res = await fetch('http://localhost:5000/alunos/importar_csv', {
        method: 'POST',
        body: fd
      });
      const data = await res.json();

      if (res.ok) {
        showAlert('success', `Importação finalizada: ${data.sucesso} inseridos, ${data.pulos} pulos, ${data.erros} erros.`);
      } else {
        showAlert('error', data.erro || 'Falha na importação.');
      }

      resultado.style.display = 'block';
      logEl.textContent = (data.relatorio || []).join('\n') || 'Sem mensagens.';
    } catch (e) {
      console.error(e);
      showAlert('error', 'Erro de comunicação com o servidor.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = original;
    }
  });
});