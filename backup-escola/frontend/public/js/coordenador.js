// js/coordenador.js
document.addEventListener('DOMContentLoaded', function () {

    // Função para carregar usuários do backend
    async function carregarUsuarios() {
        try {
            const response = await fetch('http://localhost:5000/api/usuarios', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Cargo': 'coordenador'
                }
            });

            if (!response.ok) throw new Error('Erro ao buscar usuários');

            const data = await response.json();
            preencherTabela(data.usuarios);
        } catch (err) {
            exibirMensagem('Erro ao carregar usuários: ' + err.message, 'error');
        }
    }

    // Função para preencher a tabela com os usuários (somente administradores)
    function preencherTabela(usuarios) {
        const tbody = document.querySelector('#usuariosTable tbody');
        tbody.innerHTML = '';

        usuarios.forEach(user => {
            const tr = document.createElement('tr');

            const permissoes = (typeof user.permissoes === 'string')
                               ? JSON.parse(user.permissoes || "{}")
                               : (user.permissoes || {});

            tr.innerHTML = `
                <td>${user.id}</td>
                <td>${user.nome}</td>
                <td>${user.email}</td>
                <td>${user.cargo}</td>
                <td>
                    <div class="permissoes" data-user-id="${user.id}">
                        <label><input type="checkbox" data-link="cadastro-aluno" ${permissoes['cadastro-aluno'] ? 'checked' : ''}> Cadastro de Aluno</label>
                        <label><input type="checkbox" data-link="ocorrencias" ${permissoes['ocorrencias'] ? 'checked' : ''}> Ocorrências</label>
                        <label><input type="checkbox" data-link="relatorios" ${permissoes['relatorios'] ? 'checked' : ''}> Relatórios</label>
                        <label><input type="checkbox" data-link="historico" ${permissoes['historico'] ? 'checked' : ''}> Histórico</label>
                    </div>
                    <button class="salvarPermissoesBtn btn btn-sm btn-primary" data-user-id="${user.id}">
                        Salvar Permissões
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });
    }

    // Função para atualizar cargo do usuário (se necessário)
    async function atualizarCargo(event) {
        const userId = event.target.getAttribute('data-user-id');
        const select = document.querySelector(`select[data-user-id="${userId}"]`);
        const novoCargo = select.value;

        try {
            const response = await fetch(`http://localhost:5000/api/usuarios/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cargo: novoCargo })
            });

            const data = await response.json();

            if (data.success) {
                exibirMensagem('Cargo atualizado com sucesso!', 'success');
                carregarUsuarios();
            } else {
                exibirMensagem('Erro ao atualizar cargo: ' + data.message, 'error');
            }
        } catch (err) {
            exibirMensagem('Erro ao atualizar cargo: ' + err.message, 'error');
        }
    }

    // Função para exibir mensagens
    function exibirMensagem(msg, tipo) {
        const messageDiv = document.getElementById('message');
        messageDiv.innerHTML = msg;
        messageDiv.className = tipo;
        setTimeout(() => messageDiv.innerHTML = '', 4000);
    }

    // Carregar usuários ao abrir a página
    carregarUsuarios();

    // ---------------- PERMISSÕES -----------------
    const tabela = document.getElementById("usuariosTable");

    tabela.addEventListener("click", async (e) => {
        if (e.target.classList.contains("salvarPermissoesBtn")) {
            const userId = e.target.getAttribute("data-user-id");
            const container = document.querySelector(`.permissoes[data-user-id="${userId}"]`);
            
            const permissoes = {};
            container.querySelectorAll("input[type=checkbox]").forEach(cb => {
                permissoes[cb.dataset.link] = cb.checked;
                console.log(`Permissão ${cb.dataset.link}: ${cb.checked}`); // DEBUG
            });

            try {
                console.log('Enviando permissões:', permissoes); // DEBUG
                const response = await fetch(`http://localhost:5000/usuarios/${userId}/permissoes`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ permissoes })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error("Erro ao salvar permissões: " + errorText);
                }

                const result = await response.json();
                console.log('Resposta do servidor:', result); // DEBUG
                exibirMensagem("Permissões atualizadas com sucesso!", "success");
                
                // Recarrega a página após 2 segundos para aplicar as mudanças
                setTimeout(() => {
                    carregarUsuarios();
                }, 2000);

            } catch (err) {
                console.error('Erro detalhado:', err);
                exibirMensagem("Erro ao salvar permissões: " + err.message, "error");
            }
        }
    });
});