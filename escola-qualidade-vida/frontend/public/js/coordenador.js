document.addEventListener('DOMContentLoaded', function () {

    // Função para carregar usuários do backend
    async function carregarUsuarios() {
        try {
            const response = await fetch('http://localhost:5000/api/usuarios', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Cargo': 'coordenador' // 🔹 ADICIONADO: necessário para backend liberar a lista
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

            // 🔹 ADICIONADO: Preencher checkboxes de permissões com valores do usuário
            const permissoes = user.permissoes || {};
            
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


// ---------------- PERMISSÕES -----------------
document.addEventListener("DOMContentLoaded", () => {
  const tabela = document.getElementById("usuariosTable");

  tabela.addEventListener("click", async (e) => {
    if (e.target.classList.contains("salvarPermissoesBtn")) {
      const userId = e.target.getAttribute("data-user-id");
      const container = document.querySelector(`.permissoes[data-user-id="${userId}"]`);
      
      const permissoes = {};
      container.querySelectorAll("input[type=checkbox]").forEach(cb => {
        permissoes[cb.dataset.link] = cb.checked;
      });

      try {
        const response = await fetch(`http://localhost:5000/usuarios/${userId}/permissoes`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ permissoes })
        });

        if (!response.ok) throw new Error("Erro ao salvar permissões");

        alert("Permissões atualizadas!");
      } catch (err) {
        alert("Erro: " + err.message);
      }
    }
  });
});