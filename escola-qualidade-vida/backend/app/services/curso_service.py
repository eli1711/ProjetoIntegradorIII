from app.extensions import db
from app.models.curso import Curso


def listar_cursos():
    cursos = Curso.query.order_by(Curso.nome.asc()).all()
    return [{"id": curso.id, "nome": curso.nome} for curso in cursos]


def criar_curso(dados):
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise ValueError("Nome do curso e obrigatorio.")

    curso = Curso(nome=nome)
    db.session.add(curso)
    db.session.commit()
    return {"id": curso.id, "nome": curso.nome}
