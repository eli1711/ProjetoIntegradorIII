// --- Seletores dos Elementos ---
const filtroAluno = document.getElementById('filtroAluno');
const filtroTurma = document.getElementById('filtroTurma');
const filtroPeriodo = document.getElementById('filtroPeriodo');
const filtroAndamento = document.getElementById('filtroAndamento');
const filtroTipoOcorrencia = document.getElementById('filtroTipoOcorrencia'); // NOVO: Seletor para o novo filtro
const tbody = document.querySelector('#tabelaOcorrencias tbody');
const mensagem = document.getElementById('mensagem');

// --- Funções ---

// Função para normalizar texto (remoção de acentos, etc.)
function normalizarTexto(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

// NOVO: Função para carregar os tipos de ocorrência no dropdown
function carregarTiposOcorrencia() {
    // Faz a requisição para uma NOVA ROTA no seu backend que retorna a lista de tipos
    fetch('http://10.110.18.11:5000/tipos_ocorrencia') // IMPORTANTE: Você precisará criar essa rota no seu backend
        .then(response => response.json())
        .then(tipos => {
            // Para cada tipo retornado, cria um <option> e adiciona ao <select>
            tipos.forEach(tipo => {
                const option = document.createElement('option');
                option.value = tipo; // Ex: 'roubo'
                option.textContent = tipo; // Ex: 'Roubo'
                filtroTipoOcorrencia.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar os tipos de ocorrência:', error);
            // Opcional: Adicionar uma opção de erro no select
            const option = document.createElement('option');
            option.textContent = 'Erro ao carregar tipos';
            option.disabled = true;
            filtroTipoOcorrencia.appendChild(option);
        });
}


// MODIFICADO: Função para buscar as ocorrências, agora incluindo o novo filtro
function buscarOcorrencias() {
    const alunoFiltro = normalizarTexto(filtroAluno.value);
    const turmaFiltro = normalizarTexto(filtroTurma.value);
    const periodoFiltro = filtroPeriodo.value;
    const andamentoFiltro = filtroAndamento.checked;
    const tipoFiltro = filtroTipoOcorrencia.value; // NOVO: Pega o valor do novo filtro

    let url = `http://10.110.18..11:5000/ocorrencias/listar?`;
    
    // Monta a URL com os filtros
    if (alunoFiltro) url += `aluno_nome=${alunoFiltro}&`;
    if (turmaFiltro) url += `turma=${turmaFiltro}&`;
    if (periodoFiltro) url += `periodo=${periodoFiltro}&`;
    if (andamentoFiltro) url += `andamento=${andamentoFiltro}&`;
    if (tipoFiltro) url += `tipo=${tipoFiltro}&`; // NOVO: Adiciona o parâmetro do tipo de ocorrência na URL

    // Faz a requisição para a API que retorna as ocorrências
    fetch(url)
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = ''; // Limpa as ocorrências atuais
            mensagem.textContent = ''; // Limpa a mensagem

            if (data.length === 0) {
                mensagem.textContent = 'Nenhuma ocorrência encontrada.';
                return;
            }

            // Preenche a tabela com as ocorrências filtradas
            data.forEach((ocorrencia) => {
                const linha = document.createElement('tr');
                // MODIFICADO: Adicionamos o "Tipo de Ocorrência" na tabela para visualização
                linha.innerHTML = `
                    <td>${ocorrencia.aluno_nome}</td>
                    <td>${ocorrencia.turma}</td>
                    <td>${ocorrencia.periodo}</td>
                    <td>${ocorrencia.tipo}</td> <td>${ocorrencia.andamento ? 'Em andamento' : 'Concluída'}</td>
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

// MODIFICADO: Função para limpar os filtros
function limparFiltros() {
    filtroAluno.value = '';
    filtroTurma.value = '';
    filtroPeriodo.value = '';
    filtroAndamento.checked = false;
    filtroTipoOcorrencia.value = ''; // NOVO: Reseta o filtro de tipo
    buscarOcorrencias();
}

// --- Event Listeners ---
filtroAluno.addEventListener('input', buscarOcorrencias);
filtroTurma.addEventListener('input', buscarOcorrencias);
filtroPeriodo.addEventListener('change', buscarOcorrencias);
filtroAndamento.addEventListener('change', buscarOcorrencias);
filtroTipoOcorrencia.addEventListener('change', buscarOcorrencias); // NOVO: Event listener para o novo filtro

// --- Inicialização ---
// Chama as funções para carregar os dados iniciais quando a página for carregada
document.addEventListener('DOMContentLoaded', () => {
    carregarTiposOcorrencia(); // NOVO: Carrega as opções do dropdown primeiro
    buscarOcorrencias(); // Em seguida, busca todas as ocorrências
});
