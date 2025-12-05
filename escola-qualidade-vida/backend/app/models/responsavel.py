# app/models/responsavel.py
from app.extensions import db

class Responsavel(db.Model):
    __tablename__ = "responsavel"

    id = db.Column(db.Integer, primary_key=True)

    nome_completo = db.Column(db.String(255), nullable=False)
    parentesco = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(50), nullable=False)

    endereco = db.Column(db.String(255), nullable=True)
    cep = db.Column(db.String(8), nullable=True)
    bairro = db.Column(db.String(255), nullable=True)
    municipio = db.Column(db.String(255), nullable=True)

    alunos = db.relationship("Aluno", backref="responsavel", lazy=True)
