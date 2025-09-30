document.addEventListener('DOMContentLoaded', async function () {
    const logoutBtn = document.getElementById('logoutBtn');

    // Verifica se o usuário está logado
    if (!localStorage.getItem('access_token')) {
        window.location.href = 'index.html';
        return;
    }

    // Função de logout
    logoutBtn && logoutBtn.addEventListener('click', logout);

    // ------------------- BLOQUEIO DE LINKS -------------------
    try {
        const userId = localStorage.getItem('user_id');
        const cargo = localStorage.getItem('cargo');

        console.log('Cargo:', cargo, 'UserID:', userId); // DEBUG

        // APENAS administradores têm permissões restritas
        if (cargo === "administrador" && userId) {
            console.log('Buscando permissões para administrador...'); // DEBUG
            
            const res = await fetch(`http://localhost:5000/usuarios/${userId}/permissoes`);
            
            if (res.ok) {
                const permissoes = await res.json();
                console.log('Permissões recebidas:', permissoes); // DEBUG

                // Bloqueia os links do <main> baseado nas permissões
                document.querySelectorAll("main .a").forEach(link => {
                    const id = link.id;
                    console.log(`Verificando link ${id}:`, permissoes[id]); // DEBUG
                    
                    // Se a permissão for false -> oculta o link
                    if (permissoes && permissoes[id] === false) {
                        link.style.display = "none";
                        console.log(`OCULTANDO LINK: ${id}`); // DEBUG
                    }
                });

            } else {
                console.error('Não foi possível obter permissões:', res.status);
            }
        }
        // COORDENADOR tem acesso total (não faz nada)
        else if (cargo === "coordenador") {
            console.log('Coordenador - acesso total permitido'); // DEBUG
        }

    } catch (err) {
        console.error('Erro verificando permissões:', err);
    }
});

// Função de logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('cargo');
    alert('Você foi desconectado com sucesso.');
    window.location.href = 'index.html';
}