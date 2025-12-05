// Variáveis para guardar as instâncias dos gráficos (permite destruir e recriar)
let chartInstanceAlunos = null;
let chartInstanceOcorrencias = null;
let chartInstanceEscolas = null;

// Paleta de cores baseada no CSS do SENAI
const COLORS = {
    primary: '#c40000',    // Vermelho
    secondary: '#000283',  // Azul Escuro
    success: '#27854d',    // Verde
    warning: '#ffc107',    // Amarelo
    info: '#17a2b8',       // Azul Claro
    gray: '#6c757d'        // Cinza
};

/**
 * Função principal chamada pelo render() do HTML
 */
function renderCharts(alunos, turmas, mapOcorrPorAluno) {
    
    // Verifica se o Chart.js foi carregado
    if (typeof Chart === 'undefined') {
        console.warn("Chart.js não encontrado. Verifique o CDN no HTML.");
        return;
    }

    // --- 1. PROCESSAMENTO DE DADOS ---

    // A. Contagem de Alunos por Curso
    const countCurso = {};
    alunos.forEach(a => {
        let curso = a.curso_nome || a.curso;
        // Tenta buscar nome do curso na turma se não tiver no aluno
        if (!curso && a.turma_id) {
            const t = turmas.find(tr => tr.id == a.turma_id);
            if (t) curso = t.curso_nome;
        }
        curso = curso || "Não Identificado";
        countCurso[curso] = (countCurso[curso] || 0) + 1;
    });

    // Ordena (maior para menor) e pega Top 8
    const sortedCursos = Object.entries(countCurso)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);

    // B. Contagem de Ocorrências por Curso
    const countOcorrCurso = {};
    alunos.forEach(a => {
        let curso = a.curso_nome || a.curso;
        if (!curso && a.turma_id) {
            const t = turmas.find(tr => tr.id == a.turma_id);
            if (t) curso = t.curso_nome;
        }
        curso = curso || "Outros";

        const qtd = mapOcorrPorAluno.get(a.id) || 0;
        if (qtd > 0) {
            countOcorrCurso[curso] = (countOcorrCurso[curso] || 0) + qtd;
        }
    });

    // Ordena e pega Top 8
    const sortedOcorr = Object.entries(countOcorrCurso)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);

    // C. Distribuição por Escola Integrada
    const countEscola = {};
    alunos.forEach(a => {
        const esc = a.escola_integrada || a.escola || "Não Informado";
        countEscola[esc] = (countEscola[esc] || 0) + 1;
    });

    // Top 5 escolas
    const sortedEscolas = Object.entries(countEscola)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);


    // --- 2. CRIAÇÃO DOS GRÁFICOS ---

    // Gráfico 1: Alunos por Curso (Barras Horizontais)
    const ctxAlunos = document.getElementById('chartAlunosCurso');
    if (ctxAlunos) {
        if (chartInstanceAlunos) chartInstanceAlunos.destroy();

        chartInstanceAlunos = new Chart(ctxAlunos.getContext('2d'), {
            type: 'bar',
            data: {
                labels: sortedCursos.map(i => i[0]),
                datasets: [{
                    label: 'Alunos',
                    data: sortedCursos.map(i => i[1]),
                    backgroundColor: COLORS.secondary,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y', // Deitado
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: 'Top Cursos (Qtd. Alunos)', font: { size: 16 } },
                    legend: { display: false }
                }
            }
        });
    }

    // Gráfico 2: Ocorrências por Curso (Barras Verticais)
    const ctxOcorr = document.getElementById('chartOcorrenciasCurso');
    if (ctxOcorr) {
        if (chartInstanceOcorrencias) chartInstanceOcorrencias.destroy();

        chartInstanceOcorrencias = new Chart(ctxOcorr.getContext('2d'), {
            type: 'bar',
            data: {
                labels: sortedOcorr.map(i => i[0]),
                datasets: [{
                    label: 'Ocorrências',
                    data: sortedOcorr.map(i => i[1]),
                    backgroundColor: COLORS.primary,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: 'Ocorrências por Curso', font: { size: 16 } },
                    legend: { display: false }
                }
            }
        });
    }

    // Gráfico 3: Escolas Integradas (Rosquinha)
    const ctxEscola = document.getElementById('chartEscolas');
    if (ctxEscola) {
        if (chartInstanceEscolas) chartInstanceEscolas.destroy();

        chartInstanceEscolas = new Chart(ctxEscola.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: sortedEscolas.map(i => i[0]),
                datasets: [{
                    data: sortedEscolas.map(i => i[1]),
                    backgroundColor: [COLORS.secondary, COLORS.primary, COLORS.success, COLORS.warning, COLORS.info],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: 'Origem Escolar', font: { size: 16 } },
                    legend: { position: 'bottom', labels: { boxWidth: 10, usePointStyle: true } }
                }
            }
        });
    }
}