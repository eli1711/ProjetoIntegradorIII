// Esperar o carregamento do DOM para garantir que os elementos existam
document.addEventListener("DOMContentLoaded", function() {
    const filtroMatricula = document.getElementById("filtroMatricula");
    const filtroAluno = document.getElementById("filtroAluno");
    const filtroCurso = document.getElementById("filtroCurso");  // Corrigido para filtroCurso
    const tabela = document.getElementById("tabelaAlunos").getElementsByTagName("tbody")[0];
    const informacoesAluno = document.getElementById("informacoesAluno");
    const nomeAluno = document.getElementById("nomeAluno");
    const enderecoAluno = document.getElementById("enderecoAluno");
    const idadeAluno = document.getElementById("idadeAluno");
    const responsavelAluno = document.getElementById("responsavelAluno");
    const tabelaOcorrencias = document.getElementById("tabelaOcorrencias").getElementsByTagName("tbody")[0];
    const ocorrenciasPorData = document.getElementById("ocorrenciasPorData");

    // Adiciona eventos de digitação e mudança nos campos de filtro
    [filtroMatricula, filtroAluno, filtroCurso].forEach(input => {  // Atualizado para usar filtroCurso
        input.addEventListener("input", aplicarFiltro);
        input.addEventListener("change", aplicarFiltro);
    });

    // Função para aplicar filtro de busca
    async function aplicarFiltro() {
        const matricula = filtroMatricula.value;
        const nome = filtroAluno.value;
        const curso = filtroCurso.value;  // Corrigido para buscar por curso

        const url = new URL('http://localhost:5000/alunos/buscar');  // URL corrigida para /alunos/buscar
        const params = { matricula, nome, curso };  // Incluindo o parâmetro curso

        Object.keys(params).forEach(key => params[key] && url.searchParams.append(key, params[key]));

        try {
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Erro ao buscar alunos: ${response.statusText}`);
            }

            const alunos = await response.json();
            renderizarTabela(alunos);

        } catch (error) {
            console.error("Erro ao buscar alunos:", error);
            showAlert("error", "Erro ao buscar alunos");
        }
    }

    // Função para renderizar a tabela com os dados dos alunos
    function renderizarTabela(alunos) {
        tabela.innerHTML = "";

        if (alunos.length === 0) {
            document.getElementById("mensagem").textContent = "Nenhum aluno encontrado.";
            return;
        }

        document.getElementById("mensagem").textContent = "";

        alunos.forEach(aluno => {
            const linha = tabela.insertRow();
            linha.innerHTML = `
                <td><a href="#" onclick="mostrarInformacoesAluno(${aluno.id})">${aluno.nome}</a></td>
                <td>${aluno.curso}</td>  <!-- Exibindo o curso -->
            `;
        });
    }

    // Função para mostrar as informações detalhadas de um aluno
    async function mostrarInformacoesAluno(alunoId) {
        try {
            const responseAluno = await fetch(`http://localhost:5000/alunos/${alunoId}`);

            if (!responseAluno.ok) {
                throw new Error(`Erro ao carregar informações do aluno: ${responseAluno.statusText}`);
            }

            const aluno = await responseAluno.json();

            // Exibindo as informações detalhadas
            nomeAluno.textContent = `Nome: ${aluno.nome}`;
            enderecoAluno.textContent = `Endereço: ${aluno.rua}, ${aluno.bairro}, ${aluno.cidade}`;
            idadeAluno.textContent = `Idade: ${aluno.idade}`;
            responsavelAluno.textContent = `Responsável: ${aluno.responsavel_nome || 'Não informado'}`;

            // Renderiza ocorrências
            const responseOcorrencias = await fetch(`http://localhost:5000/ocorrencias?aluno_id=${alunoId}`);
            const ocorrencias = await responseOcorrencias.json();
            renderizarOcorrencias(ocorrencias);

            // Contabiliza ocorrências por data
            renderizarOcorrenciasPorData(ocorrencias);

            informacoesAluno.style.display = "block";
        } catch (error) {
            console.error("Erro ao carregar informações do aluno:", error);
            showAlert("error", "Erro ao carregar informações do aluno");
        }
    }

    // Função para renderizar as ocorrências do aluno
    function renderizarOcorrencias(ocorrencias) {
        tabelaOcorrencias.innerHTML = "";

        if (ocorrencias.length === 0) {
            return;
        }

        ocorrencias.forEach(ocorrencia => {
            const linha = tabelaOcorrencias.insertRow();
            linha.innerHTML = `
                <td>${ocorrencia.data_ocorrencia}</td>
                <td>${ocorrencia.tipo}</td>
                <td>${ocorrencia.descricao}</td>
            `;
        });
    }

    // Função para renderizar o número de ocorrências por data
    function renderizarOcorrenciasPorData(ocorrencias) {
        const ocorrenciasCount = {};

        ocorrencias.forEach(ocorrencia => {
            const data = ocorrencia.data_ocorrencia;
            if (ocorrenciasCount[data]) {
                ocorrenciasCount[data]++;
            } else {
                ocorrenciasCount[data] = 1;
            }
        });

        let html = "<ul>";
        for (const data in ocorrenciasCount) {
            html += `<li>${data}: ${ocorrenciasCount[data]} ocorrência(s)</li>`;
        }
        html += "</ul>";

        ocorrenciasPorData.innerHTML = html;
    }

    // Função para limpar os filtros
    function limparFiltros() {
        filtroMatricula.value = "";
        filtroAluno.value = "";
        filtroCurso.value = "";  // Corrigido para limpar filtro de curso
        aplicarFiltro();
    }

    // Inicializa a tabela com todos os dados
    aplicarFiltro();
});
