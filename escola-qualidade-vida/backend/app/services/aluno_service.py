from app.models.aluno import Aluno
from app.utils.database import get_db_session

def listar_alunos():
    session = get_db_session()
    alunos = session.query(Aluno).all()
    session.close()
    return [{"id": a.id_aluno, "nome": a.nome} for a in alunos]
