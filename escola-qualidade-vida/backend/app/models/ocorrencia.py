from datetime import datetime
from app.extensions import db

class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'

    id = db.Column(db.Integer, primary_key=True)

    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)

    tipo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)

    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_ocorrencia = db.Column(db.Date, nullable=True)

    # ✅ precisa ser nullable=True para combinar com ON DELETE SET NULL
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True)

    aluno = db.relationship('Aluno', backref='ocorrencias')
    turma = db.relationship('Turma', backref='ocorrencias')

    # Constantes para os tipos de ocorrência
    TIPO_ATRASO = 'Atraso'
    TIPO_SAIDA_ANTECIPADA = 'Saída Antecipada'
    TIPO_PROBLEMA_SAUDE = 'Problema de Saúde'
    TIPO_APOIO_PSICOLOGICO = 'Apoio Psicológico- Emocional'
    TIPO_APOIO_EDUCACIONAL = 'Apoio Educacional'
    TIPO_ATENDIMENTO_EMPRESAS = 'Atendimento Empresas'
    TIPO_ATENDIMENTO_PAIS = 'Atendimento Pais e Responsáveis'
    TIPO_ATENDIMENTO_AAPM = 'Atendimento AAPM'
    TIPO_VENDA_UNIFORME = 'Venda de Uniforme'
    TIPO_OUTROS = 'Outros'

    @classmethod
    def get_tipos(cls):
        return [
            cls.TIPO_ATRASO,
            cls.TIPO_SAIDA_ANTECIPADA,
            cls.TIPO_PROBLEMA_SAUDE,
            cls.TIPO_APOIO_PSICOLOGICO,
            cls.TIPO_APOIO_EDUCACIONAL,
            cls.TIPO_ATENDIMENTO_EMPRESAS,
            cls.TIPO_ATENDIMENTO_PAIS,
            cls.TIPO_ATENDIMENTO_AAPM,
            cls.TIPO_VENDA_UNIFORME,
            cls.TIPO_OUTROS
        ]

    def to_dict(self):
        aluno_nome = None
        aluno_matricula = None
        if self.aluno:
            # tenta usar nome_completo, senão monta nome + sobrenome
            aluno_nome = getattr(self.aluno, "nome_completo", None) or (
                f"{getattr(self.aluno, 'nome', '')} {getattr(self.aluno, 'sobrenome', '')}".strip()
            )
            aluno_matricula = getattr(self.aluno, "matricula", None)

        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': aluno_nome,
            'aluno_matricula': aluno_matricula,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'data': self.data.isoformat() if self.data else None,
            'data_ocorrencia': self.data_ocorrencia.isoformat() if self.data_ocorrencia else None,
            'turma_id': self.turma_id,
            'turma_nome': self.turma.nome if self.turma else None
        }
