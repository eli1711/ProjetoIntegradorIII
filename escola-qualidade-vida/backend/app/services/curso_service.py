from app.models.curso import Curso
from app import db

def listar_cursos():
    cursos = Curso.query.all()
    return [{"id": c.id, "nome": c.nome} for c in cursos]

def criar_curso(dados):
    curso = Curso(nome=dados["nome"])
    db.session.add(curso)
    db.session.commit()
    return {"id": curso.id, "nome": curso.nome}
