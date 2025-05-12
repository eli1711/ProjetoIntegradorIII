from app import db

class Aluno(db.Model):
    __tablename__ = 'alunos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    rua = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    empregado = db.Column(db.String(10), nullable=False, default='nao')
    empresa = db.Column(db.String(100), nullable=True)
    comorbidade = db.Column(db.Text, nullable=True)
    nome_responsavel = db.Column(db.String(100), nullable=True)
    sobrenome_responsavel = db.Column(db.String(100), nullable=True)
    parentesco_responsavel = db.Column(db.String(100), nullable=True)
    telefone_responsavel = db.Column(db.String(50), nullable=True)
    foto = db.Column(db.String(255), nullable=True)  # caminho para imagem salva (upload)
