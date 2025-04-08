async function getAlunos() {
    try {
        const response = await fetch('http://localhost:8000/alunos');
        const data = await response.json();
        console.log(data);
        // Processar dados...
    } catch (error) {
        console.error('Erro ao buscar alunos:', error);
    }
}