const ocorrencias = [
    { aluno: 'João Silva', turma: '3A', periodo: 'Manhã', andamento: true, descricao: 'Briga no recreio' },
    { aluno: 'Maria Souza', turma: '2B', periodo: 'Tarde', andamento: false, descricao: 'Atraso frequente' },
    { aluno: 'Carlos Lima', turma: '3A', periodo: 'Manhã', andamento: true, descricao: 'Uso de celular em aula' },
    { aluno: 'Ana Clara', turma: '1C', periodo: 'Noite', andamento: true, descricao: 'Não fez lição' },
    { aluno: 'Fernanda Rocha', turma: '2B', periodo: 'Tarde', andamento: false, descricao: 'Falta sem justificativa' }
  ];
  
  const filtroAluno = document.getElementById('filtroAluno');
  const filtroTurma = document.getElementById('filtroTurma');
  const filtroPeriodo = document.getElementById('filtroPeriodo');
  const filtroAndamento = document.getElementById('filtroAndamento');
  const tbody = document.querySelector('#tabelaOcorrencias tbody');
  const mensagem = document.getElementById('mensagem');
  
  function normalizarTexto(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }
  
  function filtrarOcorrencias() {
    tbody.innerHTML = '';
    mensagem.textContent = '';
  
    const alunoFiltro = normalizarTexto(filtroAluno.value);
    const turmaFiltro = normalizarTexto(filtroTurma.value);
    const periodoFiltro = filtroPeriodo.value;
    const andamentoFiltro = filtroAndamento.checked;
  
    const resultados = ocorrencias.filter((o) => {
      const alunoMatch = normalizarTexto(o.aluno).includes(alunoFiltro);
      const turmaMatch = normalizarTexto(o.turma).includes(turmaFiltro);
      const periodoMatch = !periodoFiltro || o.periodo === periodoFiltro;
      const andamentoMatch = !andamentoFiltro || o.andamento;
  
      return alunoMatch && turmaMatch && periodoMatch && andamentoMatch;
    });
  
    if (resultados.length === 0) {
      mensagem.textContent = 'Nenhuma ocorrência encontrada.';
      return;
    }
  
    resultados.forEach((o, index) => {
      const linha = document.createElement('tr');
      linha.innerHTML = `
        <td>${o.aluno}</td>
        <td>${o.turma}</td>
        <td>${o.periodo}</td>
        <td>${o.andamento ? 'Em andamento' : 'Concluída'}</td>
        <td>
          <button class="btn-detalhes" data-index="${index}">Ver detalhes</button>
          <div class="descricao-completa" id="descricao-${index}">
            ${o.descricao}
          </div>
        </td>
      `;
      tbody.appendChild(linha);
    });
  
    document.querySelectorAll('.btn-detalhes').forEach((btn) => {
      btn.addEventListener('click', () => {
        const index = btn.getAttribute('data-index');
        const descricaoDiv = document.getElementById(`descricao-${index}`);
        descricaoDiv.classList.toggle('show');
        btn.textContent = descricaoDiv.classList.contains('show') ? 'Ocultar detalhes' : 'Ver detalhes';
      });
    });
  }
  
  function limparFiltros() {
    filtroAluno.value = '';
    filtroTurma.value = '';
    filtroPeriodo.value = '';
    filtroAndamento.checked = false;
    filtrarOcorrencias();
  }
  
  filtroAluno.addEventListener('input', filtrarOcorrencias);
  filtroTurma.addEventListener('input', filtrarOcorrencias);
  filtroPeriodo.addEventListener('change', filtrarOcorrencias);
  filtroAndamento.addEventListener('change', filtrarOcorrencias);
  
  filtrarOcorrencias();
  