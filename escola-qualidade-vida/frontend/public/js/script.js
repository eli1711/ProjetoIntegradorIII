async function getAlunos() {
    try {
        const apiUrl = "http://escola-qualidade-vida-backend:5000"; // Nome do serviço backend no docker-compose.yml


        const data = await response.json();
        console.log(data);
        // Processar dados...
    } catch (error) {
        console.error('Erro ao buscar alunos:', error);
    }
}

const idadeInput = document.getElementById('idade');
const responsavelDiv = document.getElementById('responsavelFields');

    function atualizarCamposResponsavel() {
        const idade = parseInt(idadeInput.value);

        if (!isNaN(idade) && idade < 18) {
            responsavelDiv.style.display = 'block';
        } else {
            responsavelDiv.style.display = 'none';
        }
    }

    idadeInput.addEventListener('input', atualizarCamposResponsavel);

    const empregado = document.getElementById('empregado');
    const desempregado = document.getElementById('desempregado');
    const empresaDiv = document.getElementById('empresaFields');

    function atualizarCamposEmpresa() {
        if (empregado.checked) {
            empresaDiv.style.display = 'block';
            desempregado.checked = false;
        } else {
            empresaDiv.style.display = 'none';
        }

        if (desempregado.checked) {
            empregado.checked = false;
            empresaDiv.style.display = 'none';
        }
    }

    empregado.addEventListener('change', atualizarCamposEmpresa);
    desempregado.addEventListener('change', atualizarCamposEmpresa);

    const temcomorbidade = document.getElementById('temcomorbidade');
    const naotemcomorbidade = document.getElementById('naotemcomorbidade');
    const comorbidadeDiv = document.getElementById('comorbidadeFields');

    function atualizarCamposComorbidade() {
        if (temcomorbidade.checked) {
            comorbidadeDiv.style.display = 'block';
            naotemcomorbidade.checked = false;
        } else {
            comorbidadeDiv.style.display = 'none';
        }

        if (desempregado.checked) {
            temcomorbidade.checked = false;
            comorbidadeDiv.style.display = 'none';
        }
    }

    temcomorbidade.addEventListener('change', atualizarCamposComorbidade);
    naotemcomorbidade.addEventListener('change', atualizarCamposComorbidade);