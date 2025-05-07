async function getAlunos() {
    try {
        const response = await fetch('http://localhost:8000/alunos');
        const data = await response.json();
        console.log(data);
        // Processar os dados recebidos de alunos
        // Aqui você pode manipular ou exibir as informações conforme necessário.
    } catch (error) {
        console.error('Erro ao buscar alunos:', error);
    }
}

// Campos de idade e responsável
const idadeInput = document.getElementById('idade');
const responsavelDiv = document.getElementById('responsavelFields');

// Atualizar campos de responsável com base na idade
function atualizarCamposResponsavel() {
    const idade = parseInt(idadeInput.value);

    if (!isNaN(idade) && idade < 18) {
        responsavelDiv.style.display = 'block';
    } else {
        responsavelDiv.style.display = 'none';
    }
}

// Escuta o evento de input para atualizar a visibilidade dos campos
idadeInput.addEventListener('input', atualizarCamposResponsavel);

// Campos de emprego e empresa
const empregado = document.getElementById('empregado');
const desempregado = document.getElementById('desempregado');
const empresaDiv = document.getElementById('empresaFields');

// Atualizar campos de empresa com base no status de emprego
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

// Escuta os eventos de mudança para atualizar a visibilidade dos campos
empregado.addEventListener('change', atualizarCamposEmpresa);
desempregado.addEventListener('change', atualizarCamposEmpresa);

// Campos de comorbidade
const temcomorbidade = document.getElementById('temcomorbidade');
const naotemcomorbidade = document.getElementById('naotemcomorbidade');
const comorbidadeDiv = document.getElementById('comorbidadeFields');

// Atualizar campos de comorbidade com base na seleção
function atualizarCamposComorbidade() {
    if (temcomorbidade.checked) {
        comorbidadeDiv.style.display = 'block';
        naotemcomorbidade.checked = false;
    } else {
        comorbidadeDiv.style.display = 'none';
    }

    if (naotemcomorbidade.checked) {
        temcomorbidade.checked = false;
        comorbidadeDiv.style.display = 'none';
    }
}

// Escuta os eventos de mudança para atualizar a visibilidade dos campos
temcomorbidade.addEventListener('change', atualizarCamposComorbidade);
naotemcomorbidade.addEventListener('change', atualizarCamposComorbidade);

// Chama a função para buscar os alunos (opcional)
getAlunos();
