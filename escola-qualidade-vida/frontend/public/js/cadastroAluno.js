document.getElementById('cadastroAlunoForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('http://localhost:5000/alunos/cadastrar-aluno', {  // Certifique-se de que a URL está correta
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: formData  // Usando FormData para envio de arquivos e dados de formulário
        });

        // Verifica se a resposta foi bem-sucedida (código 2xx)
        if (response.ok) {
            const data = await response.json(); // Espera a resposta JSON do servidor
            alert("✅ " + data.mensagem); // Alerta de sucesso
            form.reset(); // Reseta o formulário
        } else {
            const errorData = await response.json(); // Pega o erro da resposta do servidor
            alert("❌ Erro: " + (errorData.erro || 'Não foi possível cadastrar o aluno'));
        }
    } catch (error) {
        // Caso ocorra um erro durante a requisição
        console.error("Erro ao cadastrar aluno:", error);
        alert("❌ Erro inesperado no cadastro.");
    }
});
