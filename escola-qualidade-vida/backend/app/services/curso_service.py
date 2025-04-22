from app.models.curso import Curso
from app.utils.database import get_db_session

def listar_cursos():
    session = get_db_session()
    cursos = session.query(Curso).all()
    session.close()
    return [{"id": c.id_curso, "nome": c.nome} for c in cursos]

def criar_curso(dados):
    session = get_db_session()
    curso = Curso(nome=dados["nome"])
    session.add(curso)
    session.commit()
    session.refresh(curso)
    session.close()
    return {"id": curso.id_curso, "nome": curso.nome}
