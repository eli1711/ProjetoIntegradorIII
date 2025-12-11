// Função para carregar cursos
async function carregarCursos() {
  const cursoFiltro = document.getElementById('cursoFiltro');
  const response = await fetch('http://localhost:5000/cursos/');
  const cursos = await response.json();
  cursos.forEach(curso => {
    const option = document.createElement('option');
    option.value = curso.id;
    option.textContent = curso.nome;
    cursoFiltro.appendChild(option);
  });
}

// Função para carregar tipos de ocorrências
async function carregarOcorrencias() {
  const ocorrenciaFiltro = document.getElementById('ocorrenciaFiltro');
  const response = await fetch('http://localhost:5000/ocorrencias/tipos');
  const tipos = await response.json();
  tipos.forEach(tipo => {
    const option = document.createElement('option');
    option.value = tipo;
    option.textContent = tipo;
    ocorrenciaFiltro.appendChild(option);
  });
} 

async function aplicarFiltros() {
  const alunoFiltro = document.getElementById('buscaAluno').value;
  const cursoFiltro = document.getElementById('cursoFiltro').value;
  const ocorrenciaFiltro = document.getElementById('ocorrenciaFiltro').value;

  // Requisição para pegar dados filtrados
  const response = await fetch(`http://localhost:5000/dashboard?aluno=${alunoFiltro}&curso=${cursoFiltro}&ocorrencia=${ocorrenciaFiltro}`);
  const dados = await response.json();

  // Exibindo as estatísticas
  document.getElementById('kpiMediaIdade').textContent = dados.mediaIdades;
  document.getElementById('kpiPCD').textContent = dados.alunosPCD;
  document.getElementById('kpiTurmasAtivas').textContent = dados.turmasAtivas;
  document.getElementById('kpiTurmasFinalizadas').textContent = dados.turmasFinalizadas;

  // Exibindo as ocorrências
  const listaOcorrencias = document.getElementById('listaOcorrencias');
  listaOcorrencias.innerHTML = '';
  dados.ocorrencias.forEach(ocorrencia => {
    const li = document.createElement('li');
    li.textContent = `${ocorrencia.tipo} - ${ocorrencia.descricao}`;
    li.addEventListener('click', () => {
      alert(`Detalhes da Ocorrência:\n\nTipo: ${ocorrencia.tipo}\nDescrição: ${ocorrencia.descricao}`);
    });
    listaOcorrencias.appendChild(li);
  });

  // Atualizar os gráficos (Função que já existe no seu código)
  renderCharts(dados);
}

// Evento de clique no botão "Aplicar Filtros"
document.getElementById('btnAplicar').addEventListener('click', aplicarFiltros);

function renderCharts(dados) {
  // Exemplo para renderizar um gráfico de barras com os dados dos alunos por curso
  const ctx = document.getElementById('chartAlunosCurso').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Curso A', 'Curso B', 'Curso C'],  // Exemplo, substitua com os cursos reais
      datasets: [{
        label: 'Número de Alunos',
        data: [dados.alunosCursoA, dados.alunosCursoB, dados.alunosCursoC], // Substitua com os dados reais
        backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)'],
        borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)'],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}
