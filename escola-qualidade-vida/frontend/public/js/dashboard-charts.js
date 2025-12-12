// dashboard-charts.js

// Variáveis globais para os gráficos
let chartAlunosCurso = null;
let chartOcorrenciasCurso = null;
let chartEscolas = null;

// Carregar dados do dashboard
async function carregarDashboard() {
  try {
    // Mostrar indicador de carregamento
    mostrarCarregamento(true);
    
    // Pegar valores dos filtros
    const statusTurma = document.getElementById('statusTurma').value;
    const cursoFiltro = document.getElementById('cursoFiltro').value;
    const alunoFiltro = document.getElementById('buscaAluno').value.trim();
    const turmaFiltro = document.getElementById('buscaTurma').value.trim();
    
    // Construir URL com parâmetros
    let url = 'http://localhost:5000/dashboard?';
    const params = new URLSearchParams();
    
    if (statusTurma && statusTurma !== 'todas') params.append('status', statusTurma);
    if (cursoFiltro) params.append('curso', cursoFiltro);
    if (alunoFiltro) params.append('aluno', alunoFiltro);
    if (turmaFiltro) params.append('turma', turmaFiltro);
    
    url += params.toString();
    
    console.log('Buscando dados da URL:', url);
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Erro HTTP ${response.status}: ${response.statusText}`);
    }
    
    const dados = await response.json();
    console.log('Dados recebidos:', dados);
    
    // Atualizar KPIs
    atualizarKPIs(dados);
    
    // Renderizar gráficos
    if (dados.graficos) {
      renderizarGraficos(dados.graficos);
    }
    
    // Renderizar tabela de alunos
    if (dados.alunosFiltrados) {
      renderizarTabelaAlunos(dados.alunosFiltrados);
    }
    
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error);
    alert(`Erro ao carregar dados do dashboard: ${error.message}`);
  } finally {
    mostrarCarregamento(false);
  }
}

// Atualizar KPIs
function atualizarKPIs(dados) {
  // Função auxiliar para formatar números
  const formatarNumero = (valor) => {
    if (valor === undefined || valor === null) return '-';
    return Number.isInteger(valor) ? valor : valor.toFixed(1);
  };
  
  // Atualizar cada KPI
  document.getElementById('kpiTotalAlunos').textContent = formatarNumero(dados.totalAlunos);
  document.getElementById('kpiPCD').textContent = formatarNumero(dados.alunosPCD);
  document.getElementById('kpiMediaIdade').textContent = formatarNumero(dados.mediaIdade);
  document.getElementById('kpiTurmasAtivas').textContent = formatarNumero(dados.turmasAtivas);
  document.getElementById('kpiTurmasFinalizadas').textContent = formatarNumero(dados.turmasFinalizadas);
  document.getElementById('kpiOcorrencias').textContent = formatarNumero(dados.totalOcorrencias);
}

// Renderizar gráficos
function renderizarGraficos(graficos) {
  // Destruir gráficos existentes
  if (chartAlunosCurso) chartAlunosCurso.destroy();
  if (chartOcorrenciasCurso) chartOcorrenciasCurso.destroy();
  if (chartEscolas) chartEscolas.destroy();
  
  // Gráfico 1: Alunos por Curso
  const ctx1 = document.getElementById('chartAlunosCurso');
  if (ctx1) {
    const cursos = Object.keys(graficos.alunosPorCurso || {});
    const valoresCursos = Object.values(graficos.alunosPorCurso || {});
    
    // Se não houver dados, mostrar mensagem
    if (cursos.length === 0) {
      ctx1.style.display = 'none';
      ctx1.parentElement.innerHTML = '<p class="sem-dados">Nenhum dado disponível para alunos por curso</p>';
    } else {
      ctx1.style.display = 'block';
      chartAlunosCurso = new Chart(ctx1.getContext('2d'), {
        type: 'bar',
        data: {
          labels: cursos,
          datasets: [{
            label: 'Alunos por Curso',
            data: valoresCursos,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            borderRadius: 5
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            title: {
              display: true,
              text: 'Distribuição de Alunos por Curso'
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Número de Alunos'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Cursos'
              }
            }
          }
        }
      });
    }
  }
  
  // Gráfico 2: Ocorrências por Tipo
  const ctx2 = document.getElementById('chartOcorrenciasCurso');
  if (ctx2) {
    const tipos = Object.keys(graficos.ocorrenciasPorTipo || {});
    const valoresTipos = Object.values(graficos.ocorrenciasPorTipo || {});
    
    // Se não houver dados, mostrar mensagem
    if (tipos.length === 0) {
      ctx2.style.display = 'none';
      ctx2.parentElement.innerHTML = '<p class="sem-dados">Nenhuma ocorrência registrada</p>';
    } else {
      ctx2.style.display = 'block';
      chartOcorrenciasCurso = new Chart(ctx2.getContext('2d'), {
        type: 'pie',
        data: {
          labels: tipos,
          datasets: [{
            label: 'Ocorrências por Tipo',
            data: valoresTipos,
            backgroundColor: [
              'rgba(255, 99, 132, 0.6)',
              'rgba(54, 162, 235, 0.6)',
              'rgba(255, 206, 86, 0.6)',
              'rgba(75, 192, 192, 0.6)',
              'rgba(153, 102, 255, 0.6)',
              'rgba(255, 159, 64, 0.6)',
              'rgba(201, 203, 207, 0.6)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(255, 159, 64, 1)',
              'rgba(201, 203, 207, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'right'
            },
            title: {
              display: true,
              text: 'Distribuição de Ocorrências por Tipo'
            }
          }
        }
      });
    }
  }
  
  // Gráfico 3: Escolas Integradas
  const ctx3 = document.getElementById('chartEscolas');
  if (ctx3) {
    const escolas = Object.keys(graficos.escolas || {});
    const valoresEscolas = Object.values(graficos.escolas || {});
    
    // Se não houver dados, mostrar mensagem
    if (escolas.length === 0) {
      ctx3.style.display = 'none';
      ctx3.parentElement.innerHTML = '<p class="sem-dados">Nenhum dado disponível para escolas</p>';
    } else {
      ctx3.style.display = 'block';
      chartEscolas = new Chart(ctx3.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: escolas,
          datasets: [{
            label: 'Escolas Integradas',
            data: valoresEscolas,
            backgroundColor: [
              'rgba(255, 159, 64, 0.6)',
              'rgba(201, 203, 207, 0.6)',
              'rgba(75, 192, 192, 0.6)',
              'rgba(54, 162, 235, 0.6)',
              'rgba(153, 102, 255, 0.6)'
            ],
            borderColor: [
              'rgba(255, 159, 64, 1)',
              'rgba(201, 203, 207, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(153, 102, 255, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'right'
            },
            title: {
              display: true,
              text: 'Distribuição por Escola Integrada'
            }
          }
        }
      });
    }
  }
}

// Renderizar tabela de alunos
function renderizarTabelaAlunos(alunos) {
  const tbody = document.getElementById('corpoTabelaAlunos');
  if (!tbody) return;
  
  // Limpar tabela existente
  tbody.innerHTML = '';
  
  // Se não houver alunos
  if (!alunos || alunos.length === 0) {
    const row = tbody.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 8;
    cell.textContent = 'Nenhum aluno encontrado com os filtros aplicados';
    cell.style.textAlign = 'center';
    cell.style.padding = '20px';
    cell.style.color = '#666';
    return;
  }
  
  // Adicionar cada aluno na tabela
  alunos.forEach(aluno => {
    const row = tbody.insertRow();
    
    // ID
    const cellId = row.insertCell();
    cellId.textContent = aluno.id || '-';
    
    // Nome
    const cellNome = row.insertCell();
    cellNome.textContent = aluno.nome || '-';
    
    // Turma
    const cellTurma = row.insertCell();
    cellTurma.textContent = aluno.turma || '-';
    
    // Curso
    const cellCurso = row.insertCell();
    cellCurso.textContent = aluno.curso || '-';
    
    // Idade
    const cellIdade = row.insertCell();
    cellIdade.textContent = aluno.idade || '-';
    
    // Escola Integrada
    const cellEscola = row.insertCell();
    cellEscola.textContent = aluno.escola_integrada || '-';
    
    // PCD
    const cellPCD = row.insertCell();
    cellPCD.textContent = aluno.pessoa_com_deficiencia ? 'Sim' : 'Não';
    
    // Ocorrências
    const cellOcorrencias = row.insertCell();
    cellOcorrencias.textContent = aluno.ocorrencias || 0;
    
    // Adicionar classe para zebrado
    if (tbody.rows.length % 2 === 0) {
      row.classList.add('zebrado');
    }
  });
}

// Carregar cursos para o filtro
async function carregarCursos() {
  try {
    const response = await fetch('http://localhost:5000/cursos/');
    if (!response.ok) {
      throw new Error(`Erro ao buscar cursos: ${response.status}`);
    }
    
    const cursos = await response.json();
    const select = document.getElementById('cursoFiltro');
    
    if (!select) return;
    
    // Limpar opções existentes
    select.innerHTML = '<option value="">Todos os Cursos</option>';
    
    // Adicionar cursos
    cursos.forEach(curso => {
      const option = document.createElement('option');
      option.value = curso.id;
      option.textContent = curso.nome || `Curso ${curso.id}`;
      select.appendChild(option);
    });
    
    console.log(`${cursos.length} cursos carregados no filtro`);
  } catch (error) {
    console.error('Erro ao carregar cursos:', error);
    // Não mostrar alerta para evitar interromper o usuário
  }
}

// Mostrar/ocultar indicador de carregamento
function mostrarCarregamento(mostrar) {
  const btnAplicar = document.getElementById('btnAplicar');
  if (!btnAplicar) return;
  
  if (mostrar) {
    btnAplicar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
    btnAplicar.disabled = true;
  } else {
    btnAplicar.innerHTML = '<i class="fa-solid fa-filter"></i> Aplicar';
    btnAplicar.disabled = false;
  }
}

// Limpar filtros
function limparFiltros() {
  document.getElementById('buscaAluno').value = '';
  document.getElementById('buscaTurma').value = '';
  document.getElementById('statusTurma').value = 'todas';
  document.getElementById('cursoFiltro').value = '';
  
  // Recarregar dashboard
  carregarDashboard();
}

// Adicionar botão de limpar filtros
function adicionarBotaoLimpar() {
  const filtersSection = document.querySelector('.filters');
  if (!filtersSection) return;
  
  const limparBtn = document.createElement('button');
  limparBtn.id = 'btnLimpar';
  limparBtn.className = 'btn btn-limpar';
  limparBtn.innerHTML = '<i class="fa-solid fa-eraser"></i> Limpar';
  limparBtn.addEventListener('click', limparFiltros);
  
  // Adicionar ao container de filtros
  const group = document.createElement('div');
  group.className = 'group';
  group.appendChild(limparBtn);
  filtersSection.appendChild(group);
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
  console.log('Dashboard inicializando...');
  
  // Carregar cursos no filtro
  carregarCursos();
  
  // Adicionar botão de limpar filtros
  adicionarBotaoLimpar();
  
  // Carregar dados do dashboard
  carregarDashboard();
  
  // Configurar botão de aplicar
  const btnAplicar = document.getElementById('btnAplicar');
  if (btnAplicar) {
    btnAplicar.addEventListener('click', carregarDashboard);
  }
  
  // Configurar busca por Enter
  const buscaAluno = document.getElementById('buscaAluno');
  const buscaTurma = document.getElementById('buscaTurma');
  
  if (buscaAluno) {
    buscaAluno.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') carregarDashboard();
    });
  }
  
  if (buscaTurma) {
    buscaTurma.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') carregarDashboard();
    });
  }
  
  console.log('Dashboard inicializado com sucesso');
});