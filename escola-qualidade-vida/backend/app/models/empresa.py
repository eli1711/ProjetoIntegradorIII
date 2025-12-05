# app/models/empresa.py
from app.extensions import db

class Empresa(db.Model):
    __tablename__ = "empresa"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)

    alunos = db.relationship("Aluno", backref="empresa", lazy=True)
