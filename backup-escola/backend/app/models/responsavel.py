from app import db

class Responsavel(db.Model):
    __tablename__ = 'responsavel'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    parentesco = db.Column(db.String(255)) 
    telefone = db.Column(db.String(50))
    cidade = db.Column(db.String(255))
    bairro = db.Column(db.String(255))
    rua = db.Column(db.String(255))

    alunos = db.relationship('Aluno', backref='responsavel', lazy=True)
