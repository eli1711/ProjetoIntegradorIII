from app.extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.Enum('administrador', 'coordenador', 'analista'), nullable=False)

    # Campos para recuperação de senha
    token_recuperacao = db.Column(db.String(255), nullable=True)
    token_expiracao = db.Column(db.DateTime, nullable=True)

    # Permissões
    criar_aluno = db.Column(db.Boolean, nullable=False, default=False)
    ocorrencias = db.Column(db.Boolean, nullable=False, default=False)
    relatorios = db.Column(db.Boolean, nullable=False, default=False)
    historico = db.Column(db.Boolean, nullable=False, default=False)
    criar_usuario = db.Column(db.Boolean, nullable=False, default=False)
    gerenciamento_usuarios = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Usuario {self.nome}>'
