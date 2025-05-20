#backend/app/models/aluno.py

from app import db

class Aluno(db.Model):
    __tablename__ = 'aluno'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(255), nullable=False)
    rua = db.Column(db.String(255), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    empregado = db.Column(db.Enum('sim', 'nao'), nullable=False)
    mora_com_quem = db.Column(db.String(255))
    sobre_aluno = db.Column(db.Text)
    foto = db.Column(db.String(255))
    
    # Relacionamentos com as tabelas Responsável e Empresa 
    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsavel.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'))

def __init__(self, nome, sobrenome, cidade, bairro, rua, idade, empregado, mora_com_quem, sobre_aluno, foto, responsavel_id, empresa_id):
        self.nome = nome
        self.sobrenome = sobrenome
        self.cidade = cidade
        self.bairro = bairro
        self.rua = rua
        self.idade = idade
        self.empregado = empregado
        self.mora_com_quem = mora_com_quem  
        self.sobre_aluno = sobre_aluno
        self.foto = foto
        self.responsavel_id = responsavel_id 
        self.empresa_id = empresa_id         
