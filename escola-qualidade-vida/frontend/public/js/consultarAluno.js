async function consultarAluno() {
    const alunoId = document.getElementById('alunoId').value;
    const nomeAluno = document.getElementById('nomeAluno').value;
    let queryParam = '';
    if (alunoId) {
        queryParam = `id=${alunoId}`;
    } else if (nomeAluno) {
        queryParam = `nome=${nomeAluno}`;
    } else {
        alert("Informe ID ou Nome para consulta.");
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/alunos/consultar?${queryParam}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        const data = await response.json();
        if (response.ok) {
            console.log('Aluno encontrado:', data);
            // Exemplo: preencher campos na página com os dados retornados
            document.getElementById('resultado').innerText = 
                `Aluno: ${data.nome} ${data.sobrenome}, ${data.idade} anos, ${data.cidade}/${data.bairro}`;
        } else {
            alert(data.erro || "Aluno não encontrado.");
        }
    } catch (error) {
        console.error("Erro na consulta de aluno:", error);
        alert("Erro ao consultar aluno.");
    }
}
