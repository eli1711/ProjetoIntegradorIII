document.addEventListener("DOMContentLoaded", function() {
    const filtroAluno = document.getElementById("filtroAluno");
    const filtroCurso = document.getElementById("filtroCurso");
    const tabela = document.getElementById("tabelaAlunos").getElementsByTagName("tbody")[0];
    const informacoesAluno = document.getElementById("informacoesAluno");
    const nomeAluno = document.getElementById("nomeAluno");
    const enderecoAluno = document.getElementById("enderecoAluno");
    const idadeAluno = document.getElementById("idadeAluno");
    const responsavelAluno = document.getElementById("responsavelAluno");
    const tabelaOcorrencias = document.getElementById("tabelaOcorrencias").getElementsByTagName("tbody")[0];
    const ocorrenciasPorData = document.getElementById("ocorrenciasPorData");

    [filtroAluno, filtroCurso].forEach(input => {
        input.addEventListener("input", aplicarFiltro);
        input.addEventListener("change", aplicarFiltro);
    });

    async function aplicarFiltro() {
        const nome = filtroAluno.value;
        const curso = filtroCurso.value;

        const url = new URL('http://localhost:5000/alunos/buscar');
        const params = { nome, curso };

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
            alert("Erro ao buscar alunos");
        }
    }

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
                <td>${aluno.curso}</td>
            `;
        });
    }

    window.mostrarInformacoesAluno = async function(alunoId) {
        try {
            const responseAluno = await fetch(`http://localhost:5000/alunos/${alunoId}`);

            if (!responseAluno.ok) {
                throw new Error(`Erro ao carregar informações do aluno: ${responseAluno.statusText}`);
            }

            const aluno = await responseAluno.json();

            nomeAluno.textContent = `Nome: ${aluno.nome}`;
            enderecoAluno.textContent = `Endereço: ${aluno.rua}, ${aluno.bairro}, ${aluno.cidade}`;
            idadeAluno.textContent = `Idade: ${aluno.idade}`;
            responsavelAluno.textContent = `Responsável: ${aluno.responsavel_nome || 'Não informado'}`;

            const responseOcorrencias = await fetch(`http://localhost:5000/ocorrencias?aluno_id=${alunoId}`);
            const ocorrencias = await responseOcorrencias.json();

            renderizarOcorrencias(ocorrencias);
            renderizarOcorrenciasPorData(ocorrencias);

            informacoesAluno.style.display = "block";
        } catch (error) {
            console.error("Erro ao carregar informações do aluno:", error);
            alert("Erro ao carregar informações do aluno");
        }
    }

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

    window.fecharInformacoesAluno = function() {
        informacoesAluno.style.display = "none";
    }

    function limparFiltros() {
        filtroAluno.value = "";
        filtroCurso.value = "";
        aplicarFiltro();
    }

    window.limparFiltros = limparFiltros;

    aplicarFiltro();
});
