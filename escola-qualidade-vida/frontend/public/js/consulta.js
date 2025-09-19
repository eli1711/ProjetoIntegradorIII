document.addEventListener("DOMContentLoaded", function () {
    const filtroAluno = document.getElementById("filtroAluno");
    const filtroCurso = document.getElementById("filtroCurso");
    const filtroOcorrencia = document.getElementById("filtroTipoOcorrencia");
    const filtroTurma = document.getElementById("filtroTurma");
    const tabelaBody = document.getElementById("tabelaAlunos").getElementsByTagName("tbody")[0];
    const limparFiltrosBtn = document.getElementById("limparFiltrosBtn");
    const alerta = document.getElementById("alerta");

    // Função "debounce" para evitar chamadas excessivas à API enquanto o usuário digita
    function debounce(func, delay = 300) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => { func.apply(this, args); }, delay);
        };
    }

    const debouncedAplicarFiltro = debounce(aplicarFiltro);

    // Eventos que disparam a busca
    filtroAluno.addEventListener("input", debouncedAplicarFiltro);
    filtroCurso.addEventListener("input", debouncedAplicarFiltro);
    filtroOcorrencia.addEventListener("change", aplicarFiltro); // 'change' é melhor para select
    filtroTurma.addEventListener("input", debouncedAplicarFiltro);
    limparFiltrosBtn.addEventListener("click", limparFiltros);

    // Função para aplicar os filtros e chamar a API
    async function aplicarFiltro() {
        const nome = filtroAluno.value.trim();
        const curso = filtroCurso.value.trim();
        const ocorrencia = filtroOcorrencia.value.trim();
        const turma = filtroTurma.value.trim();

        const url = construirUrlComFiltros(nome, curso, ocorrencia, turma);

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Erro na rede: ${response.statusText}`);
            }
            const alunos = await response.json();
            renderizarAlunos(alunos);
        } catch (error) {
            console.error("Falha ao buscar alunos:", error);
            exibirErro("Erro ao se comunicar com o servidor.");
        }
    }

    // Constrói a URL da API garantindo que parâmetros vazios não sejam enviados
    function construirUrlComFiltros(nome, curso, ocorrencia, turma) {
        const baseUrl = 'http://localhost:5000/alunos/buscar';
        const params = new URLSearchParams();

        if (nome) params.append('nome', nome);
        if (curso) params.append('curso', curso);
        if (ocorrencia) params.append('ocorrencia', ocorrencia);
        if (turma) params.append('turma', turma);

        return `${baseUrl}?${params.toString()}`;
    }

    // Renderiza os dados na tabela
    function renderizarAlunos(alunos) {
        tabelaBody.innerHTML = '';
        alerta.style.display = "none";

        if (!alunos || alunos.length === 0) {
            exibirErro("Nenhum aluno encontrado para os filtros informados.");
            return;
        }

        alunos.forEach(aluno => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${aluno.nome}</td>
                <td>${aluno.curso}</td>
                <td>${aluno.ocorrencia || 'N/A'}</td>
                <td>${aluno.turma || 'N/A'}</td>
            `;
            tabelaBody.appendChild(tr);
        });
    }

    function exibirErro(mensagem) {
        tabelaBody.innerHTML = '';
        alerta.textContent = mensagem;
        alerta.style.display = "block";
    }

    function limparFiltros() {
        filtroAluno.value = "";
        filtroCurso.value = "";
        filtroOcorrencia.value = "";
        filtroTurma.value = "";
        aplicarFiltro();
    }

    // Carrega todos os alunos na primeira vez que a página abre
    aplicarFiltro();
});