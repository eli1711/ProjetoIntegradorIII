// script.js
const atividades = [
    "Aula de yoga semanal para relaxamento e concentração.",
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
  
  // Dropdown interativo
  const dropdownToggle = document.querySelector(".dropdown-toggle");
  const dropdownMenu = document.querySelector(".dropdown-menu");
  
  dropdownToggle.addEventListener("click", (e) => {
    e.preventDefault();
    dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
  });
  
  document.addEventListener("click", (e) => {
    if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
      dropdownMenu.style.display = "none";
    }
  });
  