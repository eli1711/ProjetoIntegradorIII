document.addEventListener("DOMContentLoaded", function () {
    // Recupera o nome e sobrenome do aluno da URL
    const urlParams = new URLSearchParams(window.location.search);
    const alunoNome = urlParams.get('nome');  // Recupera o parâmetro "nome" da URL
    const alunoSobrenome = urlParams.get('sobrenome');  // Recupera o parâmetro "sobrenome" da URL

    // Verifica se o nome e sobrenome foram passados na URL
    if (!alunoNome || !alunoSobrenome) {
        alert("Nome e sobrenome do aluno não encontrados.");
        return;
    }

    // Função para buscar as informações do aluno
    async function buscarInformacoesAluno() {
        try {
            // Requisição à API usando nome e sobrenome do aluno
            const response = await fetch(`http://localhost:5000/alunos/buscar?nome=${encodeURIComponent(alunoNome)}&sobrenome=${encodeURIComponent(alunoSobrenome)}`);
            if (!response.ok) {
                throw new Error(`Erro ao carregar informações do aluno: ${response.statusText}`);
            }

            const aluno = await response.json();

            // Verifica se o aluno foi encontrado
            if (aluno.length === 0) {
                alert("Aluno não encontrado.");
                return;
            }

            // Usando o primeiro aluno encontrado
            const alunoEncontrado = aluno[0];

            // Preenche os campos com as informações do aluno
            document.getElementById('nomeAluno').textContent = `Nome: ${alunoEncontrado.nome} ${alunoEncontrado.sobrenome || 'Sobrenome não informado'}`;

            // Construção do endereço
            const endereco = [
                alunoEncontrado.rua || '',
                alunoEncontrado.bairro || '',
                alunoEncontrado.cidade || ''
            ].filter(Boolean).join(', ') || 'Endereço não informado';
            
            document.getElementById('enderecoAluno').textContent = `Endereço: ${endereco}`;

            document.getElementById('idadeAluno').textContent = `Idade: ${alunoEncontrado.idade || 'Não informado'}`;
            document.getElementById('responsavelAluno').textContent = `Responsável: ${alunoEncontrado.responsavel_nome || 'Não informado'}`;

            // Exibindo outros campos relacionados ao aluno
            document.getElementById('mora_com_quem').textContent = `Mora com: ${alunoEncontrado.mora_com_quem || 'Não informado'}`;
            document.getElementById('sobreAluno').textContent = `Sobre o aluno: ${alunoEncontrado.sobre_aluno || 'Não informado'}`;
            document.getElementById('empregado').textContent = `Empregado: ${alunoEncontrado.empregado === 'sim' ? 'Sim' : 'Não'}`;

            // Carrega a foto do aluno, se disponível
            const fotoAluno = document.getElementById('fotoAluno');
            if (alunoEncontrado.foto) {
                fotoAluno.src = `http://localhost:8080/uploads/${alunoEncontrado.foto}`;
                fotoAluno.alt = alunoEncontrado.nome;
            } else {
                fotoAluno.alt = "Foto não disponível";
            }

            // Carrega as ocorrências do aluno (já retornadas na resposta da API)
            const ocorrencias = alunoEncontrado.ocorrencias || [];
            renderizarOcorrencias(ocorrencias);
            renderizarOcorrenciasPorData(ocorrencias);

        } catch (error) {
            console.error("Erro ao carregar informações do aluno:", error);
            alert("Erro ao carregar informações do aluno");
        }
    }

    // Função para renderizar ocorrências
    function renderizarOcorrencias(ocorrencias) {
        const tabelaOcorrencias = document.getElementById("tabelaOcorrencias").getElementsByTagName("tbody")[0];
        tabelaOcorrencias.innerHTML = "";

        if (ocorrencias.length === 0) {
            tabelaOcorrencias.innerHTML = "<tr><td colspan='3'>Nenhuma ocorrência registrada.</td></tr>";
            return;
        }

        ocorrencias.forEach(ocorrencia => {
            const linha = tabelaOcorrencias.insertRow();
            // Verifica se a data de ocorrência é válida
            const dataOcorrencia = ocorrencia.data_ocorrencia ? new Date(ocorrencia.data_ocorrencia).toLocaleDateString() : 'Data não informada';
            linha.innerHTML = `
                <td>${dataOcorrencia}</td>
                <td>${ocorrencia.tipo}</td>
                <td>${ocorrencia.descricao}</td>
            `;
        });
    }

    // Função para renderizar a contagem de ocorrências por data
    function renderizarOcorrenciasPorData(ocorrencias) {
        const ocorrenciasCount = {};

        ocorrencias.forEach(ocorrencia => {
            const data = ocorrencia.data_ocorrencia;
            if (data) {
                if (ocorrenciasCount[data]) {
                    ocorrenciasCount[data]++;
                } else {
                    ocorrenciasCount[data] = 1;
                }
            }
        });

        let html = "<ul>";
        for (const data in ocorrenciasCount) {
            html += `<li>${data}: ${ocorrenciasCount[data]} ocorrência(s)</li>`;
        }
        html += "</ul>";

        document.getElementById('ocorrenciasPorData').innerHTML = html;
    }

    // Chama a função para carregar as informações do aluno
    buscarInformacoesAluno();
});
