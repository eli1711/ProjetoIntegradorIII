from app import db

class Curso(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    # Obs: relacionamento com Aluno removido ou a ser definido quando Aluno tiver campo curso_id
