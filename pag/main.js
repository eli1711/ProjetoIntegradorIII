// script.js
const atividades = [
    
    "Oficina de alimentação saudável e consciente.",
    "Sessão de meditação guiada para redução do estresse.",
    "Encontros sobre saúde mental e emocional."
  ];
  
  const lista = document.getElementById("lista-atividades");
  atividades.forEach((atividade) => {
    const item = document.createElement("li");
    item.textContent = atividade;
    lista.appendChild(item);
  });
  