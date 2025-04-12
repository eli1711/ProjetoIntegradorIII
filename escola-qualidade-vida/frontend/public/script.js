async function getAlunos() {
    try {
        const response = await fetch('http://localhost:8000/alunos');
        const data = await response.json();
        console.log(data);
        // Processar dados...
    } catch (error) {
        console.error('Erro ao buscar alunos:', error);
    }
}

const menorCheckbox = document.getElementById('menorIdade');
    const maiorCheckbox = document.getElementById('maiorIdade');
    const responsavelDiv = document.getElementById('responsavelFields');

    function atualizarCamposResponsavel() {
        if (menorCheckbox.checked) {
            responsavelDiv.style.display = 'block';
            maiorCheckbox.checked = false;
        } else {
            responsavelDiv.style.display = 'none';
        }

        if (maiorCheckbox.checked) {
            menorCheckbox.checked = false;
            responsavelDiv.style.display = 'none';
        }
    }

    menorCheckbox.addEventListener('change', atualizarCamposResponsavel);
    maiorCheckbox.addEventListener('change', atualizarCamposResponsavel);

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