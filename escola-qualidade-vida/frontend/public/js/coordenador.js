document.addEventListener('DOMContentLoaded', function () {

    // Função para carregar usuários do backend
    async function carregarUsuarios() {
        try {
            const response = await fetch('http://localhost:5000/api/usuarios', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Erro ao buscar usuários');

            const data = await response.json();
            preencherTabela(data.usuarios);
        } catch (err) {
            exibirMensagem('Erro ao carregar usuários: ' + err.message, 'error');
        }
    }

    // Função para preencher a tabela com os usuários
    function preencherTabela(usuarios) {
        const tbody = document.querySelector('#usuariosTable tbody');
        tbody.innerHTML = '';

        usuarios.forEach(user => {
            const tr = document.createElement('tr');

            tr.innerHTML = `
                <td>${user.id}</td>
                <td>${user.nome}</td>
                <td>${user.email}</td>
                <td>${user.cargo}</td>
                <td>
                    <select data-user-id="${user.id}" class="cargoSelect">
                        <option value="coordenador" ${user.cargo === 'coordenador' ? 'selected' : ''}>Coordenador</option>
                        <option value="administrador" ${user.cargo === 'administrador' ? 'selected' : ''}>Administrador</option>
                    </select>
                    <button data-user-id="${user.id}" class="atualizarBtn">Atualizar</button>
                </td>
            `;

            tbody.appendChild(tr);
        });

        // Adicionar evento aos botões atualizar
        document.querySelectorAll('.atualizarBtn').forEach(btn => {
            btn.addEventListener('click', atualizarCargo);
        });
    }

    // Função para atualizar cargo do usuário
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
});
