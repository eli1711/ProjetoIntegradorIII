document.getElementById('buscarAlunoBtn').addEventListener('click', async function() {
    const nomeAluno = document.getElementById('nomeAluno').value;
    try {
        // Busca aluno pelo nome para obter seu ID
        const resAluno = await fetch(`/alunos/consultar?nome=${nomeAluno}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        const alunoData = await resAluno.json();
        if (!resAluno.ok) {
            alert(alunoData.erro || "Aluno não encontrado");
            return;
        }
        // Exibe dados do aluno (exemplo)
        console.log("Aluno:", alunoData);

        // Busca ocorrências (todas ou filtrar localmente por aluno)
        const resOc = await fetch('/ocorrencias/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        const ocorrencias = await resOc.json();
        if (resOc.ok) {
            // Filtra ocorrências do aluno buscado
            const ocorrenciasDoAluno = ocorrencias.filter(o => o.aluno_id === alunoData.id);
            console.log(`Ocorrências de ${nomeAluno}:`, ocorrenciasDoAluno);
            // TODO: atualizar interface com ocorrênciasDoAluno
        } else {
            alert("Erro ao obter ocorrências.");
        }
    } catch (error) {
        console.error("Erro ao buscar ocorrências:", error);
    }
});
