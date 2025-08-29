from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import Enum

class Aluno(db.Model):
    __tablename__ = 'aluno'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    #cpf = db.Column(db.String(14), unique=True, nullable=False)
    cidade = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(255), nullable=False)
    rua = db.Column(db.String(255), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    empregado = db.Column(Enum('sim', 'nao'), nullable=False)
    mora_com_quem = db.Column(db.String(255))
    sobre_aluno = db.Column(db.Text)
    foto = db.Column(db.String(255))

    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    curso = db.relationship('Curso', backref='alunos', lazy=True)

    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsavel.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'))

   
    def __init__(self, nome, sobrenome, cidade, bairro, rua, idade, empregado, mora_com_quem, sobre_aluno, foto=None, responsavel_id=None, empresa_id=None, curso_id=None):
        self.nome = nome
        self.sobrenome = sobrenome
        #self.cpf = cpf
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
        self.curso_id = curso_id

    def __repr__(self):
        return f"<Aluno {self.nome} {self.sobrenome}>"

