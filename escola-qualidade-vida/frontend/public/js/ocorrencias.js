document.addEventListener("DOMContentLoaded", function() {
  // Toggle do menu mobile
  document.getElementById('navToggle').addEventListener('click', function() {
    document.getElementById('navMenu').classList.toggle('show');
  });

  // Variáveis globais
  const buscarCpf = document.getElementById("buscar_cpf");
  const sugestoesUl = document.getElementById("sugestoes");
  const alunoSelecionadoDiv = document.getElementById("aluno_selecionado");
  const nomeExibido = document.getElementById("nome_exibido");
  const matriculaExibida = document.getElementById("matricula_exibida");
  const fotoExibida = document.getElementById("foto_exibida");
  const alunoIdInput = document.getElementById("aluno_id");
  const form = document.getElementById("ocorrenciaForm");
  const alertaDiv = document.getElementById("alerta");
  const tipoSelect = document.getElementById("tipo");

  // Carrega os tipos de ocorrência do backend
  async function carregarTiposOcorrencia() {
    try {
      const response = await fetch("http://localhost:5000/ocorrencias/tipos");
      const data = await response.json();
      
      if (response.ok && data.tipos) {
        tipoSelect.innerHTML = '<option value="" selected disabled>Selecione uma opção...</option>';
        
        data.tipos.forEach(tipo => {
          const option = document.createElement("option");
          option.value = tipo;
          option.textContent = tipo;
          tipoSelect.appendChild(option);
        });
      }
    } catch (err) {
      console.error("Erro ao carregar tipos de ocorrência:", err);
      mostrarAlerta("Erro ao carregar tipos de ocorrência", "erro");
    }
  }

  // Função para mostrar alertas
  function mostrarAlerta(mensagem, tipo = "sucesso") {
    alertaDiv.textContent = mensagem;
    alertaDiv.style.display = "block";
    alertaDiv.style.backgroundColor = tipo === "sucesso" ? "#d4edda" : "#f8d7da";
    alertaDiv.style.color = tipo === "sucesso" ? "#155724" : "#721c24";
    alertaDiv.style.border = tipo === "sucesso" ? "1px solid #c3e6cb" : "1px solid #f5c6cb";
    
    setTimeout(() => {
      alertaDiv.style.display = "none";
    }, 5000);
  }

  // Função para formatar CPF
  function formatarCPF(cpf) {
    if (!cpf) return '';
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  }

  // 🔍 Busca alunos por CPF conforme o usuário digita
  buscarCpf.addEventListener("input", async () => {
    const cpf = buscarCpf.value.trim().replace(/\D/g, '');
    sugestoesUl.innerHTML = "";
    
    if (cpf.length !== 11) {
      sugestoesUl.style.display = "none";
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/alunos/buscar?cpf=${cpf}`);
      const data = await response.json();

      if (response.ok && Array.isArray(data) && data.length > 0) {
        sugestoesUl.style.display = "block";
        data.forEach(aluno => {
          const li = document.createElement("li");
          li.textContent = `${aluno.nome} (CPF: ${formatarCPF(aluno.cpf)})`;
          li.style.cursor = "pointer";
          li.style.padding = "10px 15px";
          li.style.borderBottom = "1px solid #eee";
          li.style.transition = "background-color 0.2s";
          
          li.addEventListener("mouseover", () => {
            li.style.backgroundColor = "#f0f8ff";
          });
          
          li.addEventListener("mouseout", () => {
            li.style.backgroundColor = "";
          });
          
          li.addEventListener("click", () => selecionarAluno(aluno));
          sugestoesUl.appendChild(li);
        });
      } else {
        sugestoesUl.style.display = "none";
      }
    } catch (err) {
      console.error("Erro ao buscar alunos:", err);
      sugestoesUl.style.display = "none";
    }
  });

  // 🎯 Seleciona aluno e exibe foto
  function selecionarAluno(aluno) {
    alunoSelecionadoDiv.style.display = "flex";
    nomeExibido.textContent = aluno.nome;
    matriculaExibida.textContent = `CPF: ${formatarCPF(aluno.cpf)}`;
    alunoIdInput.value = aluno.id;

    // Monta URL da foto
    if (aluno.foto_url) {
      fotoExibida.src = aluno.foto_url;
    } else if (aluno.foto) {
      fotoExibida.src = `http://localhost:8080/uploads/${aluno.foto}`;
    } else {
      fotoExibida.src = "./img/sem-foto.png";
    }

    sugestoesUl.innerHTML = "";
    sugestoesUl.style.display = "none";
    buscarCpf.value = formatarCPF(aluno.cpf);
  }

  // 📤 Envio do formulário de ocorrência
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Validação básica: precisa ter aluno escolhido
    if (!alunoIdInput.value) {
      mostrarAlerta("Selecione um aluno antes de cadastrar a ocorrência.", "erro");
      buscarCpf.focus();
      return;
    }

    // Validação do tipo
    if (!tipoSelect.value) {
      mostrarAlerta("Selecione um tipo de ocorrência.", "erro");
      tipoSelect.focus();
      return;
    }

    // Validação da descrição
    const descricao = document.getElementById("descricao").value.trim();
    if (!descricao) {
      mostrarAlerta("A descrição da ocorrência é obrigatória.", "erro");
      document.getElementById("descricao").focus();
      return;
    }

    const payload = {
      aluno_id: Number(alunoIdInput.value),
      tipo: tipoSelect.value,
      descricao: descricao,
      data_ocorrencia: document.getElementById("data_ocorrencia").value || null
    };

    try {
      const response = await fetch("http://localhost:5000/ocorrencias/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        mostrarAlerta(data.mensagem || "Ocorrência cadastrada com sucesso!", "sucesso");
        form.reset();
        alunoSelecionadoDiv.style.display = "none";
        alunoIdInput.value = "";
        buscarCpf.value = "";
        fotoExibida.src = "";
        nomeExibido.textContent = "";
        matriculaExibida.textContent = "";
      } else {
        mostrarAlerta(data.erro || "Erro ao cadastrar ocorrência.", "erro");
        console.error("Detalhes do erro:", data.detalhes || data);
      }
    } catch (error) {
      console.error("Erro ao cadastrar ocorrência:", error);
      mostrarAlerta("Falha ao conectar com o servidor. Tente novamente.", "erro");
    }
  });

  // Carrega os tipos ao iniciar a página
  carregarTiposOcorrencia();
});