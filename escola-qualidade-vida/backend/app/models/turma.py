from app import db

class Turma(db.Model):
    __tablename__ = 'turmas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    # Obs: relacionamento com Aluno removido até que Aluno possua campo turma_id
