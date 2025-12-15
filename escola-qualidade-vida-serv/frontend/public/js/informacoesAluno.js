document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const alunoNome = urlParams.get('nome');
    const alunoSobrenome = urlParams.get('sobrenome');

    if (!alunoNome || !alunoSobrenome) {
        alert("Nome e sobrenome do aluno não encontrados.");
        return;
    }

    async function buscarInformacoesAluno() {
        try {
            const response = await fetch(`http://10.110.18.11:5000/alunos/buscar?nome=${encodeURIComponent(alunoNome)}&sobrenome=${encodeURIComponent(alunoSobrenome)}`);
            if (!response.ok) {
                throw new Error(`Erro ao carregar informações do aluno: ${response.statusText}`);
            }

            const aluno = await response.json();

            if (aluno.length === 0) {
                alert("Aluno não encontrado.");
                return;
            }

            const alunoEncontrado = aluno[0];

            // ✅ Correção: mostra somente o nome completo se o sobrenome existir
            let nomeCompleto = alunoEncontrado.nome;
            if (alunoEncontrado.sobrenome && alunoEncontrado.sobrenome.trim() !== "") {
                nomeCompleto += ` ${alunoEncontrado.sobrenome}`;
            }
            document.getElementById('nomeAluno').textContent = `Nome: ${nomeCompleto}`;

            document.getElementById('enderecoAluno').textContent = `Endereço: ${alunoEncontrado.endereco || 'Não informado'}`;
            document.getElementById('idadeAluno').textContent = `Idade: ${alunoEncontrado.idade || 'Não informado'}`;
            document.getElementById('responsavelAluno').textContent = `Responsável: ${alunoEncontrado.responsavel_nome || 'Não informado'}`;
            document.getElementById('mora_com_quem').textContent = `Mora com: ${alunoEncontrado.mora_com_quem || 'Não informado'}`;
            document.getElementById('sobreAluno').textContent = `Sobre o aluno: ${alunoEncontrado.sobre_aluno || 'Não informado'}`;
            document.getElementById('empregado').textContent = `Empregado: ${alunoEncontrado.empregado === 'sim' ? 'Sim' : 'Não'}`;

            const fotoAluno = document.getElementById('fotoAluno');
            if (alunoEncontrado.foto) {
                fotoAluno.src = `http://10.110.18.11:8080/uploads/${alunoEncontrado.foto}`;
                fotoAluno.alt = alunoEncontrado.nome;
            } else {
                fotoAluno.alt = "Foto não disponível";
            }

            const ocorrencias = alunoEncontrado.ocorrencias || [];
            renderizarOcorrencias(ocorrencias);
            renderizarOcorrenciasPorData(ocorrencias);

        } catch (error) {
            console.error("Erro ao carregar informações do aluno:", error);
            alert("Erro ao carregar informações do aluno");
        }
    }

    function renderizarOcorrencias(ocorrencias) {
        const tabelaOcorrencias = document.getElementById("tabelaOcorrencias").getElementsByTagName("tbody")[0];
        tabelaOcorrencias.innerHTML = "";

        if (ocorrencias.length === 0) {
            tabelaOcorrencias.innerHTML = "<tr><td colspan='3'>Nenhuma ocorrência registrada.</td></tr>";
            return;
        }

        ocorrencias.forEach(ocorrencia => {
            const linha = tabelaOcorrencias.insertRow();
            linha.innerHTML = `
                <td>${ocorrencia.data_ocorrencia || 'Data não informada'}</td>
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

        document.getElementById('ocorrenciasPorData').innerHTML = html;
    }

    buscarInformacoesAluno();
});
