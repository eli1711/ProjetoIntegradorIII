document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('cadastroAlunoForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        console.log('Formulário enviado'); // Verifique se isso aparece no console

        const alunoData = {
            nome: document.getElementById('name').value,
            sobrenome: document.getElementById('sobrenome').value,
            cidade: document.getElementById('cidade').value,
            bairro: document.getElementById('bairro').value,
            rua: document.getElementById('rua').value,
            idade: document.getElementById('idade').value,
            empregado: document.getElementById('empregado').checked ? 'sim' : 'nao',
            coma_com_quem: document.getElementById('coma_com_quem').value,
            comorbidade: document.getElementById('comorbidade').value,
        };

        const formData = new FormData();
        Object.keys(alunoData).forEach(key => {
            formData.append(key, alunoData[key]);
        });

        const fotoInput = document.getElementById('imagem');
        if (fotoInput.files.length > 0) {
            formData.append('foto', fotoInput.files[0]);
        }

        try {
            const response = await fetch('http://localhost:5000/alunos/cadastrar', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (response.ok) {
                alert('Aluno cadastrado com sucesso!');
                window.location.href = 'dashboard.html';
            } else {
                alert(`Erro: ${data.erro || 'Erro ao cadastrar o aluno'}`);
            }
        } catch (error) {
            alert('Erro de conexão com o servidor');
            console.error('Erro ao cadastrar aluno:', error);
        }
    });
});
