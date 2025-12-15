from app.models.aluno import Aluno
from app import db

def listar_alunos():
    alunos = Aluno.query.all()
    return [{"id": a.id, "nome": a.nome} for a in alunos]

def cadastrar_aluno(data):
    aluno = Aluno(
        nome=data['nome'],
        sobrenome=data['sobrenome'],
        cidade=data['cidade'],
        bairro=data['bairro'],
        rua=data['rua'],
        idade=data['idade'],
        empregado=data['empregado'],
        empresa=data.get('empresa'),
        comorbidade=data.get('comorbidade'),
        nome_responsavel=data.get('nomeResponsavel'),
        sobrenome_responsavel=data.get('sobrenomeResponsavel'),
        parentesco_responsavel=data.get('parentescoResponsavel'),
        telefone_responsavel=data.get('telefoneResponsavel')
    )

    # Salvar no banco de dados
    db.session.add(aluno)
    db.session.commit()
    return aluno
