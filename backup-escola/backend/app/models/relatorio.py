from flask_sqlalchemy import SQLAlchemy

# Instância do SQLAlchemy que será inicializada na fábrica da aplicação
db = SQLAlchemy()

class Aluno(db.Model):
    __tablename__ = 'alunos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, index=True)
    curso = db.Column(db.String(120), nullable=False, index=True)
    turma = db.Column(db.String(50), nullable=True)
    ocorrencia = db.Column(db.String(200), nullable=True, default='Nenhuma')

    def to_dict(self):
        """Converte o objeto Aluno para um dicionário, útil para a resposta JSON."""
        return {
            'id': self.id,
            'nome': self.nome,
            'curso': self.curso,
            'turma': self.turma,
            'ocorrencia': self.ocorrencia
        }