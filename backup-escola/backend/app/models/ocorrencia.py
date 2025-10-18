from datetime import datetime
from app.extensions import db

class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'

    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_ocorrencia = db.Column(db.Date, nullable=True)  # novo campo

    aluno = db.relationship('Aluno', backref='ocorrencias')
