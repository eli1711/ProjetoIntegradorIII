document.addEventListener("DOMContentLoaded", () => {
  const inputBusca = document.getElementById("buscar_nome");
  const sugestoes = document.getElementById("sugestoes");
  const nomeExibido = document.getElementById("nome_exibido");
  const fotoExibida = document.getElementById("foto_exibida");
  const alunoIdInput = document.getElementById("aluno_id");
  const alunoSelecionado = document.getElementById("aluno_selecionado");
  const alertaDiv = document.getElementById("alerta");

  inputBusca.addEventListener("input", async () => {
    const termo = inputBusca.value.trim();
    sugestoes.innerHTML = "";

    if (termo.length < 2) return;

    const resposta = await fetch(`http://localhost:5000/alunos/buscar?nome=${encodeURIComponent(termo)}`);
    const alunos = await resposta.json();

    alunos.forEach(aluno => {
      const li = document.createElement("li");
      li.textContent = aluno.nome;
      li.style.cursor = "pointer";
      li.style.padding = "4px";
      li.addEventListener("click", () => {
        inputBusca.value = aluno.nome;
        alunoIdInput.value = aluno.id;
        nomeExibido.textContent = aluno.nome;
        fotoExibida.src = `http://localhost:8080/uploads/${aluno.foto}`;
        alunoSelecionado.style.display = "block";
        sugestoes.innerHTML = "";
      });
      sugestoes.appendChild(li);
    });
  });

  document.getElementById("ocorrenciaForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;

    const dados = {
      aluno_id: alunoIdInput.value,
      tipo: form.tipo.value,
      descricao: form.descricao.value,
      data_ocorrencia: form.data_ocorrencia.value || null
    };

    try {
      const res = await fetch("http://localhost:5000/ocorrencias/cadastrar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados)
      });

      const resultado = await res.json();
      alertaDiv.style.display = "block";
      alertaDiv.innerText = resultado.mensagem || resultado.erro;
      alertaDiv.style.backgroundColor = res.ok ? "#d4edda" : "#f8d7da";
      alertaDiv.style.color = res.ok ? "#155724" : "#721c24";

      if (res.ok) form.reset();
    } catch (err) {
      alertaDiv.style.display = "block";
      alertaDiv.innerText = "Erro ao enviar ocorrência.";
      alertaDiv.style.backgroundColor = "#f8d7da";
      alertaDiv.style.color = "#721c24";
    }
  });
});
