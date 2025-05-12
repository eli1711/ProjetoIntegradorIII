document.getElementById('cadastroAlunoForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('http://localhost:5000/alunos/cadastrar', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (response.ok) {
            alert("✅ " + data.mensagem);
            form.reset();
        } else {
            alert("❌ Erro: " + (data.erro || 'Não foi possível cadastrar o aluno'));
        }
    } catch (error) {
        console.error("Erro ao cadastrar aluno:", error);
        alert("❌ Erro inesperado no cadastro.");
    }
});
