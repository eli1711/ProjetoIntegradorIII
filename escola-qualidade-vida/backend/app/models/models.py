from app import db

class Responsavel(db.Model):
    __tablename__ = 'responsavel'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    parentesco = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=True)
    cidade = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(255), nullable=False)
    rua = db.Column(db.String(255), nullable=False)

    # Relacionamento com Aluno
    alunos = db.relationship('Aluno', backref='responsavel', lazy=True)

    def __repr__(self):
        return f"<Responsavel {self.nome} {self.sobrenome}>"

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=True)
    telefone = db.Column(db.String(50), nullable=True)
    cidade = db.Column(db.String(255), nullable=True)
    bairro = db.Column(db.String(255), nullable=True)
    rua = db.Column(db.String(255), nullable=True)

    # Relacionamento com Aluno
    alunos = db.relationship('Aluno', backref='empresa', lazy=True)

    def __repr__(self):
        return f"<Empresa {self.nome}>"

class Aluno(db.Model):
    __tablename__ = 'alunos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(255), nullable=False)
    rua = db.Column(db.String(255), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    empregado = db.Column(db.Enum('sim', 'nao'), nullable=False)
    coma_com_quem = db.Column(db.String(255), nullable=True)
    comorbidade = db.Column(db.Text, nullable=True)
    foto = db.Column(db.String(255), nullable=True)
    descricao_comorbidade = db.Column(db.Text, nullable=True)

    # Relacionamentos com Responsavel e Empresa
    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsavel.id'), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=True)

    # Relacionamento de um para muitos
    responsavel = db.relationship('Responsavel', backref=db.backref('alunos', lazy=True))
    empresa = db.relationship('Empresa', backref=db.backref('alunos', lazy=True))

    def __repr__(self):
        return f"<Aluno {self.nome} {self.sobrenome}>"
