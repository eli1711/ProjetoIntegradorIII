async function consultarAluno() {
    const alunoId = document.getElementById('alunoId').value;  // Obtendo o ID do aluno ou nome do formulário
    const alunoNome = document.getElementById('alunoNome').value;

    let url = 'http://localhost:5000/consultar/aluno?';
    
    if (alunoId) {
        url += `id=${alunoId}`;
    } else if (alunoNome) {
        url += `nome=${alunoNome}`;
    } else {
        alert('Por favor, insira um ID ou nome de aluno');
        return;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (response.ok) {
            console.log('Aluno encontrado:', data);
            // Aqui você pode exibir os dados do aluno na interface
        } else {
            console.error('Erro:', data.erro);
            alert(data.erro);
        }
    } catch (error) {
        console.error('Erro ao consultar aluno:', error);
    }
}

// Evento de consulta
document.getElementById('consultarButton').addEventListener('click', consultarAluno);
