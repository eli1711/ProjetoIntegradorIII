from app.models.turma import Turma
from app import db

def listar_turmas():
    turmas = Turma.query.all()
    return [{"id": t.id, "nome": t.nome} for t in turmas]

def criar_turma(dados):
    turma = Turma(nome=dados["nome"])
    db.session.add(turma)
    db.session.commit()
    return {"id": turma.id, "nome": turma.nome}
