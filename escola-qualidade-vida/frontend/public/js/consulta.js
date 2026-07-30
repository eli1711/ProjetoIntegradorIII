document.addEventListener("DOMContentLoaded", function () {
  const filtroAluno = document.getElementById("filtroAluno");
  const filtroCurso = document.getElementById("filtroCurso");
  const filtroOcorrencia = document.getElementById("filtroTipoOcorrencia");
  const filtroTurma = document.getElementById("filtroTurma");
  const tabelaBody = document.getElementById("tabelaAlunos").getElementsByTagName("tbody")[0];
  const limparFiltrosBtn = document.getElementById("limparFiltrosBtn");
  const alerta = document.getElementById("alerta");

  function debounce(func, delay = 300) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), delay);
    };
  }

  async function carregarTiposOcorrencia() {
    if (!filtroOcorrencia) return;
    try {
      const response = await fetch("/ocorrencias/tipos");
      const data = await response.json();
      const tipos = Array.isArray(data.tipos) ? data.tipos : [];

      filtroOcorrencia.innerHTML = "";
      const todos = document.createElement("option");
      todos.value = "";
      todos.textContent = "Todos os Tipos";
      filtroOcorrencia.appendChild(todos);

      tipos.forEach((tipo) => {
        const option = document.createElement("option");
        option.value = tipo;
        option.textContent = tipo;
        filtroOcorrencia.appendChild(option);
      });
    } catch (error) {
      console.error("Falha ao carregar tipos de ocorrencia:", error);
    }
  }

  function construirUrlComFiltros() {
    const params = new URLSearchParams();
    const nome = filtroAluno.value.trim();
    const curso = filtroCurso.value.trim();
    const ocorrencia = filtroOcorrencia.value.trim();
    const turma = filtroTurma.value.trim();

    if (nome) params.append("nome", nome);
    if (curso) params.append("curso", curso);
    if (ocorrencia) params.append("ocorrencia", ocorrencia);
    if (turma) params.append("turma", turma);
    params.append("limit", "100");

    return `/alunos/buscar?${params.toString()}`;
  }

  async function aplicarFiltro() {
    try {
      const response = await fetch(construirUrlComFiltros());
      const alunos = await response.json();

      if (!response.ok) {
        exibirErro(alunos.erro || "Erro ao buscar alunos.");
        return;
      }

      renderizarAlunos(alunos);
    } catch (error) {
      console.error("Falha ao buscar alunos:", error);
      exibirErro("Erro ao se comunicar com o servidor.");
    }
  }

  function renderizarAlunos(alunos) {
    tabelaBody.innerHTML = "";
    alerta.style.display = "none";

    if (!Array.isArray(alunos) || alunos.length === 0) {
      exibirErro("Nenhum aluno encontrado para os filtros informados.");
      return;
    }

    alunos.forEach((aluno) => {
      const tr = document.createElement("tr");
      const totalOcorrencias = Array.isArray(aluno.ocorrencias) ? aluno.ocorrencias.length : 0;

      [
        aluno.nome || aluno.nome_completo || "Nao informado",
        aluno.curso || "N/A",
        String(totalOcorrencias),
        aluno.turma || aluno.turma_nome || "N/A",
      ].forEach((valor) => {
        const td = document.createElement("td");
        td.textContent = valor;
        tr.appendChild(td);
      });

      tr.addEventListener("click", () => abrirModalComDetalhes(aluno));
      tabelaBody.appendChild(tr);
    });
  }

  function abrirModalComDetalhes(aluno) {
    const modal = document.getElementById("informacoesAluno");
    if (!modal) return;

    document.getElementById("nomeAluno").textContent = `Nome: ${aluno.nome || aluno.nome_completo || "Nao informado"}`;
    document.getElementById("enderecoAluno").textContent = `Endereco: ${[
      aluno.rua,
      aluno.bairro,
      aluno.cidade,
    ].filter(Boolean).join(", ") || "Nao informado"}`;
    document.getElementById("idadeAluno").textContent = `Nascimento: ${aluno.data_nascimento || "Nao informado"}`;
    document.getElementById("responsavelAluno").textContent = `Matricula: ${aluno.matricula || "Nao informada"}`;

    const tbodyOcorrencias = document.querySelector("#tabelaOcorrencias tbody");
    tbodyOcorrencias.innerHTML = "";

    const ocorrencias = Array.isArray(aluno.ocorrencias) ? aluno.ocorrencias : [];
    if (ocorrencias.length === 0) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 3;
      td.textContent = "Nenhuma ocorrencia registrada.";
      tr.appendChild(td);
      tbodyOcorrencias.appendChild(tr);
    } else {
      ocorrencias.forEach((ocorrencia) => {
        const tr = document.createElement("tr");
        [
          ocorrencia.data_ocorrencia || ocorrencia.data || "Nao informada",
          ocorrencia.tipo || "Nao informado",
          ocorrencia.descricao || "Sem descricao",
        ].forEach((valor) => {
          const td = document.createElement("td");
          td.textContent = valor;
          tr.appendChild(td);
        });
        tbodyOcorrencias.appendChild(tr);
      });
    }

    renderizarContagemPorData(ocorrencias);
    modal.style.display = "block";
  }

  function renderizarContagemPorData(ocorrencias) {
    const container = document.getElementById("ocorrenciasPorData");
    container.innerHTML = "";

    const contagem = ocorrencias.reduce((acc, ocorrencia) => {
      const data = ocorrencia.data_ocorrencia || "Sem data";
      acc[data] = (acc[data] || 0) + 1;
      return acc;
    }, {});

    Object.entries(contagem).forEach(([data, total]) => {
      const p = document.createElement("p");
      p.textContent = `${data}: ${total}`;
      container.appendChild(p);
    });
  }

  function exibirErro(mensagem) {
    tabelaBody.innerHTML = "";
    alerta.textContent = mensagem;
    alerta.style.display = "block";
  }

  function limparFiltros() {
    filtroAluno.value = "";
    filtroCurso.value = "";
    filtroOcorrencia.value = "";
    filtroTurma.value = "";
    aplicarFiltro();
  }

  window.fecharInformacoesAluno = function fecharInformacoesAluno() {
    const modal = document.getElementById("informacoesAluno");
    if (modal) modal.style.display = "none";
  };

  const debouncedAplicarFiltro = debounce(aplicarFiltro);
  filtroAluno.addEventListener("input", debouncedAplicarFiltro);
  filtroCurso.addEventListener("input", debouncedAplicarFiltro);
  filtroOcorrencia.addEventListener("change", aplicarFiltro);
  filtroTurma.addEventListener("input", debouncedAplicarFiltro);
  limparFiltrosBtn.addEventListener("click", limparFiltros);

  carregarTiposOcorrencia();
  aplicarFiltro();
});
