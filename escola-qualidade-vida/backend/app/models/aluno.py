from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy import Enum

class Aluno(db.Model):
    __tablename__ = 'aluno'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    matricula = db.Column(db.String(255), nullable=False, unique=True)
    cidade = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(255), nullable=False)
    rua = db.Column(db.String(255), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    empregado = db.Column(Enum('sim', 'nao'), nullable=False)
    mora_com_quem = db.Column(db.String(255))
    sobre_aluno = db.Column(db.Text)
    foto = db.Column(db.String(255))
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'))
    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsavel.id'))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'))
    telefone = db.Column(db.String(255))
    data_nascimento = db.Column(db.Date)
    linha_atendimento = db.Column(Enum('CAI', 'CT', 'CST'), nullable=False)
    curso = db.Column(db.String(255))
    turma = db.Column(db.String(255))
    data_inicio_curso = db.Column(db.Date)
    empresa_contratante = db.Column(db.String(255))
    escola_integrada = db.Column(Enum('SESI', 'SEDUC', 'Nenhuma'), nullable=False)
    pessoa_com_deficiencia = db.Column(db.Boolean, default=False)
    outras_informacoes = db.Column(db.Text)

    curso_relacionado = db.relationship('Curso', backref='alunos', lazy=True)

    def __init__(self, nome, sobrenome, matricula, cidade, bairro, rua, idade, empregado,
                 mora_com_quem=None, sobre_aluno=None, foto=None, telefone=None,
                 data_nascimento=None, linha_atendimento=None, curso=None, turma=None,
                 data_inicio_curso=None, empresa_contratante=None, escola_integrada=None,
                 pessoa_com_deficiencia=False, outras_informacoes=None,
                 responsavel_id=None, empresa_id=None, curso_id=None):
        self.nome = nome
        self.sobrenome = sobrenome
        self.matricula = matricula
        self.cidade = cidade
        self.bairro = bairro
        self.rua = rua
        self.idade = idade
        self.empregado = empregado
        self.mora_com_quem = mora_com_quem
        self.sobre_aluno = sobre_aluno
        self.foto = foto
        self.telefone = telefone
        self.data_nascimento = data_nascimento
        self.linha_atendimento = linha_atendimento
        self.curso = curso
        self.turma = turma
        self.data_inicio_curso = data_inicio_curso
        self.empresa_contratante = empresa_contratante
        self.escola_integrada = escola_integrada
        self.pessoa_com_deficiencia = pessoa_com_deficiencia
        self.outras_informacoes = outras_informacoes
        self.responsavel_id = responsavel_id
        self.empresa_id = empresa_id
        self.curso_id = curso_id

    def __repr__(self):
        return f"<Aluno {self.nome} {self.sobrenome}>"
