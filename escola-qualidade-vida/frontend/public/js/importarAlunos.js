// js/importarAlunos.js
document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('arquivo');
  const btn = document.getElementById('btnImportar');
  const alertaDiv = document.getElementById('alerta');
  const resultado = document.getElementById('resultado');
  const logEl = document.getElementById('log');

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
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Importando...';

    try {
      const res = await fetch('http://localhost:5000/alunos/importar_csv', {
        method: 'POST',
        body: fd
      });
      const data = await res.json();

      if (res.ok) {
        showAlert(
          'success',
          `Importação finalizada: ${data.sucesso} alunos inseridos, ${data.pulos} pulos, ${data.erros} erros.`
        );
      } else {
        let errorMsg = data.erro || 'Falha na importação.';
        if (data.faltando) {
          errorMsg += ` Faltando campos obrigatórios: ${data.faltando.join(', ')}`;
        }
        showAlert('error', errorMsg);
      }

      resultado.style.display = 'block';
      if (data.relatorio && Array.isArray(data.relatorio)) {
        logEl.textContent = data.relatorio.join('\n');
      } else {
        logEl.textContent = 'Sem mensagens no relatório.';
      }
    } catch (e) {
      console.error(e);
      showAlert('error', 'Erro de comunicação com o servidor.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = original;
    }
  });
});