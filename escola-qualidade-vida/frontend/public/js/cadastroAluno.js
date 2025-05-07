document.getElementById('cadastroAlunoForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const alunoData = {
        nome: document.getElementById('nome').value,
        turma_id: document.getElementById('turma_id').value,
        curso_id: document.getElementById('curso_id').value,
        periodo: document.getElementById('periodo').value,
        nome_responsavel: document.getElementById('nome_responsavel').value,
        celular_responsavel: document.getElementById('celular_responsavel').value
    };

    const response = await fetch('/alunos/cadastrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alunoData)
    });

    const result = await response.json();

    if (response.ok) {
        alert('Aluno cadastrado com sucesso!');
    } else {
        alert(`Erro: ${result.detail}`);
    }
});
