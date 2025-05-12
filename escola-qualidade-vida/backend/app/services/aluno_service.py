from app.models.aluno import Aluno

def listar_alunos():
    alunos = Aluno.query.all()
    return [{"id": a.id, "nome": a.nome} for a in alunos]
