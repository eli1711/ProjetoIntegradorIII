async function getAlunos() {
    try {
        const apiUrl = "http://escola-qualidade-vida-backend:5000"; // Nome do serviço backend no docker-compose.yml


        const data = await response.json();
        console.log(data);
        // Processar dados...
    } catch (error) {
        console.error('Erro ao buscar alunos:', error);
    }
}