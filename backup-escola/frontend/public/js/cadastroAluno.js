document.addEventListener("DOMContentLoaded", function () {
    const idadeInput = document.getElementById("idade");
    const empregadoRadios = document.querySelectorAll('input[name="empregado"]');
    const responsavelSection = document.getElementById("responsavelSection");
    const empresaSection = document.getElementById("empresaSection");
    const alertaDiv = document.getElementById("alerta");
    const form = document.getElementById("cadastroAlunoForm");

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

    verificarCadastroResponsavel();
    verificarCadastroEmpresa();

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;

        // Verifica se todos os campos obrigatórios estão preenchidos
        const obrigatorios = ['nome', 'sobrenome', 'cidade', 'bairro', 'rua', 'idade', 'curso'];
        let erro = false;
        
        obrigatorios.forEach(campo => {
            if (!form[campo].value) {
                erro = true;
                showAlert("error", `O campo ${campo} é obrigatório.`);
            }
        });

        if (erro) {
            return; // Evita que o formulário seja enviado se algum campo obrigatório estiver vazio
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Cadastrando...';

        try {
            const response = await fetch("http://localhost:5000/cadastro/alunos", {
                method: "POST",
                body: new FormData(form),
            });

            const data = await response.json();

            if (response.ok) {
                showAlert("success", data.mensagem || "Aluno cadastrado com sucesso!");
                form.reset();
                verificarCadastroResponsavel();
                verificarCadastroEmpresa();
            } else {
                showAlert("error", data.erro || "Erro ao cadastrar aluno");
            }
        } catch (err) {
            console.error(err);
            showAlert("error", "Erro inesperado no envio do formulário.");
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });

    function showAlert(tipo, mensagem) {
        alertaDiv.style.display = "block";
        alertaDiv.innerText = mensagem;
        alertaDiv.style.backgroundColor = tipo === "success" ? "#d4edda" : "#f8d7da";
        alertaDiv.style.color = tipo === "success" ? "#155724" : "#721c24";
        alertaDiv.style.border = tipo === "success" ? "1px solid #c3e6cb" : "1px solid #f5c6cb";
        alertaDiv.style.marginTop = "20px";
        alertaDiv.style.padding = "10px";
        alertaDiv.style.borderRadius = "4px";

        setTimeout(() => {
            alertaDiv.style.display = "none";
        }, 5000);
    }
});
