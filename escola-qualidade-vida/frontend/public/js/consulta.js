document.addEventListener("DOMContentLoaded", function () {
    const filtroAluno = document.getElementById("filtroAluno");
    const filtroCurso = document.getElementById("filtroCurso");
    const suggestionsList = document.getElementById("suggestionsList");
    const alerta = document.getElementById("alerta");
    const tabela = document.getElementById("tabelaAlunos").getElementsByTagName("tbody")[0];
    const limparFiltrosBtn = document.getElementById("limparFiltrosBtn");

    filtroAluno.addEventListener("input", aplicarFiltro);
    filtroAluno.addEventListener("change", aplicarFiltro);
    filtroCurso.addEventListener("input", aplicarFiltro);
    limparFiltrosBtn.addEventListener("click", limparFiltros);

    // Função para aplicar filtros
    async function aplicarFiltro() {
        const nome = filtroAluno.value.trim();
        const curso = filtroCurso.value.trim();

        // Verifica se algum filtro foi preenchido corretamente
        if (nome.length < 3 && curso.length < 3) {
            esconderSugestoes();
            renderizarAlunos([]);  // Exibe tabela vazia se nenhum filtro válido
            return;
        }

        const url = construirUrlComFiltros(nome, curso);
        try {
            const alunos = await obterDadosDaApi(url);
            renderizarAlunos(alunos);
        } catch (error) {
            exibirErro("Erro ao buscar alunos, tente novamente mais tarde.");
        }
    }

    // Função para construir a URL de requisição com parâmetros
    function construirUrlComFiltros(nome, curso) {
        const url = new URL('http://localhost:5000/alunos/buscar');
        const params = new URLSearchParams();

        // Só adiciona o parâmetro se ele não estiver vazio
        if (nome) params.append('nome', nome);
        if (curso) params.append('curso', curso);

        // Se não houver filtros, retorna a URL sem parâmetros (opcional)
        if (params.toString()) {
            url.search = params.toString();
        }

        return url;
    }

    // Função para fazer a requisição da API e obter os dados
    async function obterDadosDaApi(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Erro ao buscar alunos: ${response.statusText}`);
        return response.json();
    }

    // Função para renderizar os alunos na tabela
    function renderizarAlunos(alunos) {
        tabela.innerHTML = ''; // Limpar a tabela antes de adicionar novos dados
        if (alunos.length === 0) {
            exibirErro("Nenhum aluno encontrado.");
            return;
        }

        alunos.forEach(aluno => {
            const tr = document.createElement("tr");

            // Dividindo o nome completo para separar nome e sobrenome
            const nomeCompleto = aluno.nome.trim().split(" ");
            const nome = nomeCompleto[0];  // Primeiro nome
            const sobrenome = nomeCompleto.slice(1).join(" ");  // O restante é o sobrenome

            // Criando o link com os parâmetros de nome e sobrenome
            tr.innerHTML = `
                <td><a href="informacoesAluno.html?nome=${encodeURIComponent(nome)}&sobrenome=${encodeURIComponent(sobrenome)}">${aluno.nome}</a></td>
                <td>${aluno.curso}</td>
            `;
            tabela.appendChild(tr);
        });

        esconderSugestoes(); // Esconde as sugestões após exibir os resultados
    }

    // Função para exibir mensagens de erro
    function exibirErro(mensagem) {
        alerta.textContent = mensagem;
        alerta.style.display = "block";
    }

    // Função para esconder as sugestões
    function esconderSugestoes() {
        suggestionsList.style.display = "none";
    }

    // Função para limpar filtros
    function limparFiltros() {
        filtroAluno.value = "";
        filtroCurso.value = "";
        aplicarFiltro(); // Atualizar a tabela ao limpar os filtros
    }
});
