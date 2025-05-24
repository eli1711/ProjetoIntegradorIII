from app import db

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(255), nullable=False)

    # Correção: Nome da classe com A maiúsculo
    alunos = db.relationship('Aluno', backref='empresa', lazy=True)
