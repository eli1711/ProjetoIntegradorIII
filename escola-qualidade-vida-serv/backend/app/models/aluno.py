# app/models/aluno.py
from app.extensions import db

def only_digits(s: str | None) -> str | None:
    if not s:
        return None
    digits = "".join(ch for ch in str(s) if ch.isdigit())
    return digits or None


class Aluno(db.Model):
    __tablename__ = "aluno"

    id = db.Column(db.Integer, primary_key=True)
    
    # ✅ CPF OBRIGATÓRIO (conforme sua tabela)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    
    # ✅ Campo nome_completo (opcional)
    nome_completo = db.Column(db.String(255), nullable=True)
    
    # ✅ Campo nome_social (adicionado)
    nome_social = db.Column(db.String(255), nullable=True)
    
    # Campos originais da sua tabela
    nome = db.Column(db.String(255), nullable=False)
    sobrenome = db.Column(db.String(255), nullable=False)
    matricula = db.Column(db.String(255), nullable=False)

    cidade = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(255), nullable=False)
    rua = db.Column(db.String(255), nullable=False)

    idade = db.Column(db.Integer, nullable=False)
    empregado = db.Column(db.String(10), nullable=False)

    mora_com_quem = db.Column(db.String(255), nullable=True)
    sobre_aluno = db.Column(db.Text, nullable=True)

    foto = db.Column(db.String(255), nullable=True)

    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=True)
    turma_id = db.Column(db.Integer, db.ForeignKey("turmas.id"), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresa.id"), nullable=True)
    responsavel_id = db.Column(db.Integer, db.ForeignKey("responsavel.id"), nullable=True)

    telefone = db.Column(db.String(255), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)

    linha_atendimento = db.Column(db.String(10), nullable=False)
    curso = db.Column(db.String(255), nullable=True)
    turma = db.Column(db.String(255), nullable=True)

    data_inicio_curso = db.Column(db.Date, nullable=True)
    empresa_contratante = db.Column(db.String(255), nullable=True)

    escola_integrada = db.Column(db.String(20), nullable=False)

    pessoa_com_deficiencia = db.Column(db.Boolean, nullable=True)
    outras_informacoes = db.Column(db.Text, nullable=True)

    curso_relacionado = db.relationship("Curso", foreign_keys=[curso_id], lazy=True)
    turma_relacionada = db.relationship("Turma", foreign_keys=[turma_id], lazy=True)
    empresa_relacionada = db.relationship("Empresa", foreign_keys=[empresa_id], lazy=True)

    def normalize(self):
        self.telefone = only_digits(self.telefone)
        self.cpf = only_digits(self.cpf)
        
        # Se tiver nome_completo mas nome/sobrenome estiverem vazios, preenche
        if self.nome_completo and (not self.nome or not self.sobrenome):
            partes = self.nome_completo.strip().split(' ', 1)
            self.nome = partes[0] if partes else ''
            self.sobrenome = partes[1] if len(partes) > 1 else ''
        # Se não tiver nome_completo, constrói a partir de nome+sobrenome
        elif not self.nome_completo and self.nome and self.sobrenome:
            self.nome_completo = f"{self.nome} {self.sobrenome}"
        
        # Se tiver nome_social mas não tiver nome_completo, mantém nome_social separado
        if self.nome_social and not self.nome_completo:
            self.nome_completo = f"{self.nome} {self.sobrenome}"

    def __repr__(self):
        nome_exibicao = self.nome_social or self.nome
        return f"<Aluno {self.id} {nome_exibicao} {self.sobrenome}>"