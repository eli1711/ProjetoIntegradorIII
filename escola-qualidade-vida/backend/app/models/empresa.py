from app.extensions import db

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255))
    telefone = db.Column(db.String(50))
    cidade = db.Column(db.String(255))
    bairro = db.Column(db.String(255))
    rua = db.Column(db.String(255))

    alunos = db.relationship('Aluno', backref='empresa', lazy=True)
