const filtroAluno = document.getElementById('filtroAluno');
const filtroTurma = document.getElementById('filtroTurma');
const filtroPeriodo = document.getElementById('filtroPeriodo');
const filtroAndamento = document.getElementById('filtroAndamento');
const tbody = document.querySelector('#tabelaOcorrencias tbody');
const mensagem = document.getElementById('mensagem');

// Função para normalizar texto (remoção de acentos, por exemplo)
function normalizarTexto(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

// Função para realizar a requisição GET para buscar as ocorrências do backend
function buscarOcorrencias() {
    const alunoFiltro = normalizarTexto(filtroAluno.value);
    const turmaFiltro = normalizarTexto(filtroTurma.value);
    const periodoFiltro = filtroPeriodo.value;
    const andamentoFiltro = filtroAndamento.checked;

    let url = `http://localhost:5000/ocorrencias/listar?`;
    
    // Monta a URL com os filtros
    if (alunoFiltro) {
        url += `aluno_nome=${alunoFiltro}&`;
    }
    if (turmaFiltro) {
        url += `turma=${turmaFiltro}&`;
    }
    if (periodoFiltro) {
        url += `periodo=${periodoFiltro}&`;
    }
    if (andamentoFiltro) {
        url += `andamento=${andamentoFiltro}&`;
    }

    // Faz a requisição para a API que retorna as ocorrências
    fetch(url)
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';  // Limpa as ocorrências atuais
            mensagem.textContent = '';  // Limpa a mensagem

            if (data.length === 0) {
                mensagem.textContent = 'Nenhuma ocorrência encontrada.';
                return;
            }

            // Preenche a tabela com as ocorrências filtradas
            data.forEach((ocorrencia) => {
                const linha = document.createElement('tr');
                linha.innerHTML = `
                    <td>${ocorrencia.aluno_nome}</td>
                    <td>${ocorrencia.turma}</td>
                    <td>${ocorrencia.periodo}</td>
                    <td>${ocorrencia.andamento ? 'Em andamento' : 'Concluída'}</td>
                    <td>
                        <button class="btn-detalhes" data-id="${ocorrencia.id}">Ver detalhes</button>
                        <div class="descricao-completa" id="descricao-${ocorrencia.id}">
                            ${ocorrencia.descricao}
                        </div>
                    </td>
                `;
                tbody.appendChild(linha);
            });

            // Adiciona os eventos de "Ver detalhes"
            document.querySelectorAll('.btn-detalhes').forEach((btn) => {
                btn.addEventListener('click', () => {
                    const id = btn.getAttribute('data-id');
                    const descricaoDiv = document.getElementById(`descricao-${id}`);
                    descricaoDiv.classList.toggle('show');
                    btn.textContent = descricaoDiv.classList.contains('show') ? 'Ocultar detalhes' : 'Ver detalhes';
                });
            });
        })
        .catch(error => {
            console.error('Erro ao carregar ocorrências:', error);
            mensagem.textContent = 'Erro ao carregar as ocorrências.';
        });
}

// Função para limpar os filtros e recarregar as ocorrências
function limparFiltros() {
    filtroAluno.value = '';
    filtroTurma.value = '';
    filtroPeriodo.value = '';
    filtroAndamento.checked = false;
    buscarOcorrencias();
}

// Event listeners para aplicar os filtros
filtroAluno.addEventListener('input', buscarOcorrencias);
filtroTurma.addEventListener('input', buscarOcorrencias);
filtroPeriodo.addEventListener('change', buscarOcorrencias);
filtroAndamento.addEventListener('change', buscarOcorrencias);

// Chama a função para carregar as ocorrências pela primeira vez
buscarOcorrencias();
