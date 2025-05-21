from app import db

class Responsavel(db.Model):
    __tablename__ = 'responsavel'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    
    # Relacionamento com a tabela Aluno
    alunos = db.relationship('aluno', backref='responsavel', lazy=True)
