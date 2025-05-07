document.getElementById('buscarAlunoBtn').addEventListener('click', async function() {
    const nomeAluno = document.getElementById('buscaAluno').value;

    const response = await fetch(`/alunos/consultar?nome=${nomeAluno}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });

    const result = await response.json();

    if (response.ok && result.alunos.length > 0) {
        const aluno = result.alunos[0]; // Considerando o primeiro aluno encontrado
        document.getElementById('aluno_id').value = aluno.id_aluno;
        document.getElementById('dadosAluno').innerHTML = `
            <p><strong>Nome:</strong> ${aluno.nome}</p>
            <p><strong>Turma:</strong> ${aluno.turma_id}</p>
            <p><strong>Curso:</strong> ${aluno.curso_id}</p>
            <p><strong>Período:</strong> ${aluno.periodo}</p>
        `;
    } else {
        alert('Aluno não encontrado!');
    }
});

document.getElementById('cadastroOcorrenciaForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const ocorrenciaData = {
        aluno_id: document.getElementById('aluno_id').value,
        tipo: document.getElementById('tipo').value,
        descricao: document.getElementById('descricao').value,
        usuario_id: document.getElementById('usuario_id').value
    };

    const response = await fetch('/ocorrencias/registrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ocorrenciaData)
    });

    const result = await response.json();

    if (response.ok) {
        alert('Ocorrência registrada com sucesso!');
    } else {
        alert(`Erro: ${result.detail}`);
    }
});
