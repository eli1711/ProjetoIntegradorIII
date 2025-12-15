document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("cadastroAlunoForm");
    const alertaDiv = document.getElementById("alerta");
    const nascInput = document.getElementById("data_nascimento");
    const responsavelSection = document.getElementById("responsavelSection");
    const pneCheckbox = document.getElementById("pne");
    const pneSection = document.getElementById("pneSection");

    function showAlert(tipo, mensagem) {
        alertaDiv.style.display = "block";
        alertaDiv.textContent = mensagem;
        alertaDiv.className = tipo === "success" ? "alert-success" : "alert-error";
        setTimeout(() => (alertaDiv.style.display = "none"), 6000);
    }

    function calcIdade(yyyy_mm_dd) {
        if (!yyyy_mm_dd) return null;
        const [y,m,d] = yyyy_mm_dd.split("-").map(Number);
        if (!y || !m || !d) return null;
        const hoje = new Date();
        let idade = hoje.getFullYear() - y;
        const mm = hoje.getMonth() + 1;
        const dd = hoje.getDate();
        if (mm < m || (mm === m && dd < d)) idade--;
        return idade;
    }

    function toggleResponsavel() {
        const idade = calcIdade(nascInput.value);
        const menor = (idade !== null && idade < 18);
        responsavelSection.style.display = menor ? "block" : "none";

        // torna obrigatórios se menor
        ["responsavel_nome_completo","responsavel_parentesco","responsavel_telefone"].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.required = menor;
            }
        });
    }

    function togglePNE() {
        pneSection.style.display = pneCheckbox.checked ? "block" : "none";
    }

    nascInput.addEventListener("change", toggleResponsavel);
    pneCheckbox.addEventListener("change", togglePNE);

    toggleResponsavel();
    togglePNE();

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const btn = form.querySelector('button[type="submit"]');
        const original = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cadastrando...';

        try {
            const fd = new FormData(form);
            
            // Validação básica de campos obrigatórios
            const obrigatorios = ['nome_completo', 'cpf', 'matricula', 'data_nascimento', 
                                 'endereco', 'cep', 'bairro', 'municipio', 'curso', 'tipo_curso', 'turma'];
            let erros = [];
            
            obrigatorios.forEach(campo => {
                const input = form.querySelector(`[name="${campo}"]`);
                if (input && !input.value.trim()) {
                    erros.push(campo.replace('_', ' '));
                }
            });
            
            if (erros.length > 0) {
                showAlert("error", `Preencha os campos obrigatórios: ${erros.join(', ')}`);
                btn.disabled = false;
                btn.innerHTML = original;
                return;
            }

            const res = await fetch(form.action, { method: "POST", body: fd });
            const data = await res.json();

            if (res.ok) {
                showAlert("success", data.mensagem || "Aluno cadastrado com sucesso!");
                form.reset();
                toggleResponsavel();
                togglePNE();
            } else {
                showAlert("error", data.erro || "Erro no cadastro");
            }
        } catch (err) {
            console.error(err);
            showAlert("error", "Erro inesperado ao enviar o formulário.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = original;
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("cadastroAlunoForm");
    const alertaDiv = document.getElementById("alerta");
    const nascInput = document.getElementById("data_nascimento");
    const responsavelSection = document.getElementById("responsavelSection");
    const pneCheckbox = document.getElementById("pne");
    const pneSection = document.getElementById("pneSection");

    function showAlert(tipo, mensagem) {
        alertaDiv.style.display = "block";
        alertaDiv.textContent = mensagem;
        alertaDiv.className = tipo === "success" ? "alert-success" : "alert-error";
        setTimeout(() => (alertaDiv.style.display = "none"), 6000);
    }

    function calcIdade(yyyy_mm_dd) {
        if (!yyyy_mm_dd) return null;
        const [y,m,d] = yyyy_mm_dd.split("-").map(Number);
        if (!y || !m || !d) return null;
        const hoje = new Date();
        let idade = hoje.getFullYear() - y;
        const mm = hoje.getMonth() + 1;
        const dd = hoje.getDate();
        if (mm < m || (mm === m && dd < d)) idade--;
        return idade;
    }

    function toggleResponsavel() {
        const idade = calcIdade(nascInput.value);
        const menor = (idade !== null && idade < 18);
        responsavelSection.style.display = menor ? "block" : "none";

        // torna obrigatórios se menor
        ["responsavel_nome_completo","responsavel_parentesco","responsavel_telefone"].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.required = menor;
            }
        });
    }

    function togglePNE() {
        pneSection.style.display = pneCheckbox.checked ? "block" : "none";
    }

    nascInput.addEventListener("change", toggleResponsavel);
    pneCheckbox.addEventListener("change", togglePNE);

    toggleResponsavel();
    togglePNE();

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const btn = form.querySelector('button[type="submit"]');
        const original = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cadastrando...';

        try {
            const fd = new FormData(form);
            
            // Validação básica de campos obrigatórios
            const obrigatorios = ['nome_completo', 'cpf', 'matricula', 'data_nascimento', 
                                 'endereco', 'cep', 'bairro', 'municipio', 'curso', 'tipo_curso', 'turma'];
            let erros = [];
            
            obrigatorios.forEach(campo => {
                const input = form.querySelector(`[name="${campo}"]`);
                if (input && !input.value.trim()) {
                    erros.push(campo.replace('_', ' '));
                }
            });
            
            if (erros.length > 0) {
                showAlert("error", `Preencha os campos obrigatórios: ${erros.join(', ')}`);
                btn.disabled = false;
                btn.innerHTML = original;
                return;
            }

            const res = await fetch(form.action, { method: "POST", body: fd });
            const data = await res.json();

            if (res.ok) {
                showAlert("success", data.mensagem || "Aluno cadastrado com sucesso!");
                form.reset();
                toggleResponsavel();
                togglePNE();
            } else {
                showAlert("error", data.erro || "Erro no cadastro");
            }
        } catch (err) {
            console.error(err);
            showAlert("error", "Erro inesperado ao enviar o formulário.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = original;
        }
    });
});