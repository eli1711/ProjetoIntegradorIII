from app.models.turma import Turma
from app.utils.database import get_db_session

def listar_turmas():
    session = get_db_session()
    turmas = session.query(Turma).all()
    session.close()
    return [{"id": t.id_turma, "nome": t.nome} for t in turmas]

def criar_turma(dados):
    session = get_db_session()
    turma = Turma(nome=dados["nome"])
    session.add(turma)
    session.commit()
    session.refresh(turma)
    session.close()
    return {"id": turma.id_turma, "nome": turma.nome}
