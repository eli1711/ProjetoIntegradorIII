// Dados de exemplo (substitua por dados reais ou carregue via API)
const alunos = [
    { id: "101", nome: "João", turma: "A", periodo: "Manhã",},
    { id: "102", nome: "Maria", turma: "B", periodo: "Tarde",},
    { id: "103", nome: "João", turma: "C", periodo: "Noite",},
    { id: "104", nome: "Ana", turma: "A", periodo: "Manhã",},
  ];
  
  const filtroMatricula = document.getElementById("filtroMatricula");
  const filtroAluno = document.getElementById("filtroAluno");
  const filtroTurma = document.getElementById("filtroTurma");
  const filtroPeriodo = document.getElementById("filtroPeriodo");
  const tabela = document.getElementById("tabelaAlunos").getElementsByTagName("tbody")[0];
  
  // Adiciona eventos de digitação e mudança nos campos de filtro
  [filtroMatricula, filtroAluno, filtroTurma, filtroPeriodo].forEach(input => {
    input.addEventListener("input", aplicarFiltro);
    input.addEventListener("change", aplicarFiltro);
  });
  
  function aplicarFiltro() {
    const id = filtroMatricula.value.toLowerCase();
    const nome = filtroAluno.value.toLowerCase();
    const turma = filtroTurma.value.toLowerCase();
    const periodo = filtroPeriodo.value;
  
    const filtrados = alunos.filter(aluno => {
      return (
        aluno.id.toLowerCase().includes(id) &&
        aluno.nome.toLowerCase().includes(nome) &&
        aluno.turma.toLowerCase().includes(turma) &&
        (periodo === "" || aluno.periodo === periodo)
      );
    });
  
    renderizarTabela(filtrados);
  }
  
  function renderizarTabela(dados) {
    tabela.innerHTML = "";
  
    if (dados.length === 0) {
      document.getElementById("mensagem").textContent = "Nenhum aluno encontrado.";
      return;
    }
  
    document.getElementById("mensagem").textContent = "";
  
    dados.forEach(aluno => {
      const linha = tabela.insertRow();
      linha.innerHTML = `
        <td>${aluno.nome}</td>
        <td>${aluno.turma}</td>
        <td>${aluno.periodo}</td>
      `;
    });
  }
  
  function limparFiltros() {
    filtroMatricula.value = "";
    filtroAluno.value = "";
    filtroTurma.value = "";
    filtroPeriodo.value = "";
    renderizarTabela(alunos);
    document.getElementById("mensagem").textContent = "";
  }
  
  // Inicializa a tabela com todos os dados
  renderizarTabela(alunos);
  