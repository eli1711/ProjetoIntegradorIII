from app.extensions import db

class Turma(db.Model):
    __tablename__ = 'turmas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    semestre = db.Column(db.String(1), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=True)  # preenche só no fim do semestre
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)

    curso = db.relationship('Curso', backref='turmas', lazy=True)

    def __repr__(self):
        return f"<Turma {self.nome} (sem {self.semestre})>"
