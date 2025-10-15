// coordenador.js - Versão corrigida
document.addEventListener('DOMContentLoaded', function() {
    carregarUsuarios();
});

async function carregarUsuarios() {
    try {
        const response = await fetch('http://localhost:5000/api/usuarios');
        const data = await response.json();
        
        if (response.ok) {
            exibirUsuarios(data.usuarios);
        } else {
            console.error('Erro ao carregar usuários:', data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

function exibirUsuarios(usuarios) {
    const lista = document.getElementById('listaUsuarios');
    lista.innerHTML = '';

    usuarios.forEach(usuario => {
        const li = document.createElement('li');
        li.innerHTML = `
            <strong>${usuario.nome}</strong> - ${usuario.email} 
            <span class="cargo">(${usuario.cargo})</span>
        `;
        lista.appendChild(li);
    });
}

// REMOVA completamente as funções de permissões que não existem mais