from app.extensions import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(50), nullable=False, default='coordenador')
    permissoes = db.Column(db.String(255))

    # Campos para recuperação de senha
    token_recuperacao = db.Column(db.String(255), nullable=True)
    token_expiracao = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'