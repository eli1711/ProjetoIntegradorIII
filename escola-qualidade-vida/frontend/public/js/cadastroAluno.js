document.addEventListener("DOMContentLoaded", function () {
    const idadeInput = document.getElementById("idade");
    const empregadoRadios = document.querySelectorAll('input[name="empregado"]');
    const responsavelSection = document.getElementById("responsavelSection");
    const empresaSection = document.getElementById("empresaSection");

    function verificarCadastroResponsavel() {
        const idade = parseInt(idadeInput.value);
        if (!isNaN(idade) && idade < 18) {
            responsavelSection.style.display = "block";
        } else {
            responsavelSection.style.display = "none";
        }
    }

    function verificarCadastroEmpresa() {
        const empregadoSelecionado = document.querySelector('input[name="empregado"]:checked');
        if (empregadoSelecionado && empregadoSelecionado.value === "sim") {
            empresaSection.style.display = "block";
        } else {
            empresaSection.style.display = "none";
        }
    }

    idadeInput.addEventListener("change", verificarCadastroResponsavel);
    empregadoRadios.forEach(radio => {
        radio.addEventListener("change", verificarCadastroEmpresa);
    });

    // Executa na carga inicial para restaurar o estado (útil em formulários com reenvio automático)
    verificarCadastroResponsavel();
    verificarCadastroEmpresa();
});
