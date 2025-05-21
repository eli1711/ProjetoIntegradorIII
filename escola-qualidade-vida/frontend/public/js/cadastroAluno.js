document.getElementById('cadastroAlunoForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    
    // Verifica se o token existe
    if (!localStorage.getItem('access_token')) {
        alert("❌ Você precisa estar logado para cadastrar um aluno");
        return;
    }

    // Mostra feedback visual
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Cadastrando...';

    try {
        const response = await fetch('http://localhost:5000/cadastro/aluno', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: new FormData(form)
        });

        if (response.ok) {
            const data = await response.json();
            showAlert('success', data.mensagem || 'Aluno cadastrado com sucesso!');
            form.reset();
        } else {
            const errorData = await response.json();
            showAlert('danger', errorData.erro || 'Erro ao cadastrar aluno');
        }
    } catch (error) {
        console.error("Erro ao cadastrar aluno:", error);
        showAlert('danger', 'Erro inesperado no cadastro.');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
});

function showAlert(type, message) {
    // Implementação de um alerta mais bonito (pode usar Bootstrap ou outro framework)
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.prepend(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}