// js/cadastroAluno.js - JavaScript otimizado para cadastro de alunos

document.addEventListener("DOMContentLoaded", function () {
    // Elementos do DOM
    const idadeInput = document.getElementById("idade");
    const empregadoRadios = document.querySelectorAll('input[name="empregado"]');
    const responsavelSection = document.getElementById("responsavelSection");
    const empresaSection = document.getElementById("empresaSection");
    const deficienciaSection = document.getElementById("deficienciaSection");
    const deficienciaCheckbox = document.getElementById("pessoa_com_deficiencia");
    const alertaDiv = document.getElementById("alerta");
    const form = document.getElementById("cadastroAlunoForm");
    const cursoSelect = document.getElementById("curso");
    const turmaSelect = document.getElementById("turma_id");
    const telefoneInput = document.getElementById("telefone");

    // Elementos de navegação
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    // Máscara para telefone
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 11) {
                if (value.length <= 2) {
                    value = value.replace(/^(\d{0,2})/, '($1');
                } else if (value.length <= 6) {
                    value = value.replace(/^(\d{2})(\d{0,4})/, '($1) $2');
                } else if (value.length <= 10) {
                    value = value.replace(/^(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
                } else {
                    value = value.replace(/^(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
                }
                e.target.value = value;
            }
        });
    }

    // Funções de validação de formulário
    function verificarCadastroResponsavel() {
        const idade = parseInt(idadeInput.value);
        responsavelSection.style.display = !isNaN(idade) && idade < 18 ? "block" : "none";
    }

    function verificarCadastroEmpresa() {
        const empregado = document.querySelector('input[name="empregado"]:checked');
        empresaSection.style.display = empregado && empregado.value === "sim" ? "block" : "none";
    }

    function verificarDeficiencia() {
        deficienciaSection.style.display = deficienciaCheckbox.checked ? "block" : "none";
    }

    // Carregamento de cursos e turmas
    async function loadCursos() {
        try {
            const res = await fetch("http://localhost:5000/cursos/");
            
            if (!res.ok) {
                throw new Error(`Erro HTTP: ${res.status}`);
            }
            
            const lista = await res.json();
            cursoSelect.innerHTML = '<option value="">Selecione</option>';

            if (Array.isArray(lista) && lista.length) {
                lista.forEach(c => {
                    const opt = document.createElement("option");
                    opt.value = String(c.id);
                    opt.textContent = c.nome;
                    cursoSelect.appendChild(opt);
                });
            } else {
                cursoSelect.innerHTML = '<option value="">Nenhum curso cadastrado</option>';
            }
        } catch (e) {
            console.error("Erro ao carregar cursos:", e);
            cursoSelect.innerHTML = '<option value="">Erro ao carregar cursos</option>';
            showAlert("error", "Erro ao carregar lista de cursos");
        }
    }

    async function carregarTurmasPorCurso(cursoId) {
        turmaSelect.disabled = true;
        turmaSelect.innerHTML = '<option value="">Carregando...</option>';

        if (!cursoId) {
            turmaSelect.innerHTML = '<option value="">Selecione o curso primeiro</option>';
            turmaSelect.disabled = true;
            return;
        }

        try {
            const res = await fetch(`http://localhost:5000/turmas/por_curso?curso_id=${encodeURIComponent(cursoId)}`);
            
            if (!res.ok) {
                throw new Error(`Erro HTTP: ${res.status}`);
            }
            
            const turmas = await res.json();

            if (Array.isArray(turmas) && turmas.length) {
                turmaSelect.innerHTML = '<option value="">Selecione</option>';
                turmas.forEach(t => {
                    const label = `${t.nome} (Sem ${t.semestre})`;
                    const option = document.createElement("option");
                    option.value = t.id;
                    option.textContent = label;
                    turmaSelect.appendChild(option);
                });
                turmaSelect.disabled = false;
            } else {
                turmaSelect.innerHTML = '<option value="">Nenhuma turma ativa para este curso</option>';
                turmaSelect.disabled = true;
            }
        } catch (e) {
            console.error("Erro ao carregar turmas:", e);
            turmaSelect.innerHTML = '<option value="">Erro ao carregar turmas</option>';
            turmaSelect.disabled = true;
        }
    }

    // Sistema de alertas
    function showAlert(tipo, mensagem) {
        alertaDiv.style.display = "block";
        alertaDiv.textContent = mensagem;
        alertaDiv.className = tipo === "success" ? "alert-success" : "alert-error";
        
        // Scroll suave para o alerta
        alertaDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        setTimeout(() => {
            alertaDiv.style.display = "none";
        }, 5000);
    }

    // Validação de formulário
    function validarFormulario() {
        const camposObrigatorios = [
            { id: 'nome', nome: 'Nome' },
            { id: 'sobrenome', nome: 'Sobrenome' },
            { id: 'matricula', nome: 'Matrícula' },
            { id: 'cidade', nome: 'Cidade' },
            { id: 'bairro', nome: 'Bairro' },
            { id: 'rua', nome: 'Rua' },
            { id: 'idade', nome: 'Idade' },
            { id: 'data_nascimento', nome: 'Data de Nascimento' },
            { id: 'curso', nome: 'Curso' },
            { id: 'turma_id', nome: 'Turma' },
            { id: 'linha_atendimento', nome: 'Linha de Atendimento' },
            { id: 'escola_integrada', nome: 'Escola Integrada' }
        ];

        for (const campo of camposObrigatorios) {
            const elemento = document.getElementById(campo.id);
            if (!elemento || !elemento.value.trim()) {
                showAlert("error", `O campo "${campo.nome}" é obrigatório.`);
                elemento?.focus();
                return false;
            }
        }

        // Validação de idade mínima
        const idade = parseInt(idadeInput.value);
        if (idade < 14) {
            showAlert("error", "A idade mínima para cadastro é 14 anos.");
            idadeInput.focus();
            return false;
        }

        // Validação de responsável para menores de idade
        if (idade < 18) {
            const responsavelCampos = [
                'nomeResponsavel',
                'sobrenomeResponsavel',
                'parentescoResponsavel',
                'telefone_responsavel'
            ];

            for (const campo of responsavelCampos) {
                const elemento = document.getElementById(campo);
                if (!elemento || !elemento.value.trim()) {
                    showAlert("error", `Para menores de idade, o campo "${campo.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}" do responsável é obrigatório.`);
                    elemento?.focus();
                    return false;
                }
            }
        }

        return true;
    }

    // Envio do formulário
    async function enviarFormulario(e) {
        e.preventDefault();
        
        if (!validarFormulario()) {
            return;
        }

        const btn = form.querySelector('button[type="submit"]');
        const original = btn.innerHTML;
        
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cadastrando...';

        try {
            const fd = new FormData(form);
            
            // Garante que o telefone está no payload
            const tel = (telefoneInput.value || "").trim();
            fd.set("telefone", tel);

            const res = await fetch(form.action, { 
                method: "POST", 
                body: fd 
            });
            
            const data = await res.json();
            
            if (res.ok) {
                showAlert("success", data.mensagem || "Aluno cadastrado com sucesso!");
                form.reset();
                
                // Reset dos estados das seções condicionais
                verificarCadastroResponsavel();
                verificarCadastroEmpresa();
                verificarDeficiencia();
                
                // Recarrega cursos e turmas
                await loadCursos();
            } else {
                showAlert("error", data.erro || "Erro no cadastro do aluno");
            }
        } catch (err) {
            console.error("Erro no envio:", err);
            showAlert("error", "Erro de conexão. Verifique sua internet e tente novamente.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = original;
        }
    }

    // Navegação responsiva
    function setupNavegacao() {
        if (!navToggle || !navMenu) return;

        // Toggle menu mobile
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('show');
            const icon = this.querySelector('i');
            if (navMenu.classList.contains('show')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });

        // Fechar menu ao clicar em um link (mobile)
        const navLinks = document.querySelectorAll('nav a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 992) {
                    navMenu.classList.remove('show');
                    const icon = navToggle.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        });

        // Adicionar classe active ao link da página atual
        const currentPage = window.location.pathname.split('/').pop();
        navLinks.forEach(link => {
            const linkHref = link.getAttribute('href');
            if (linkHref === currentPage || 
                (currentPage === '' && linkHref === './principal.html') ||
                (currentPage === 'index.html' && linkHref === './principal.html')) {
                link.classList.add('active');
            }
        });
    }

    // Inicialização
    function inicializar() {
        // Event listeners para seções condicionais
        idadeInput.addEventListener("change", verificarCadastroResponsavel);
        empregadoRadios.forEach(r => r.addEventListener("change", verificarCadastroEmpresa));
        deficienciaCheckbox.addEventListener("change", verificarDeficiencia);

        // Carregamento de dados
        loadCursos().then(() => {
            if (cursoSelect.value) {
                carregarTurmasPorCurso(cursoSelect.value);
            }
        });

        cursoSelect.addEventListener("change", () => carregarTurmasPorCurso(cursoSelect.value));

        // Form submission
        form.addEventListener("submit", enviarFormulario);

        // Navegação
        setupNavegacao();

        // Estado inicial das seções condicionais
        verificarCadastroResponsavel();
        verificarCadastroEmpresa();
        verificarDeficiencia();
    }

    // Iniciar a aplicação
    inicializar();
});