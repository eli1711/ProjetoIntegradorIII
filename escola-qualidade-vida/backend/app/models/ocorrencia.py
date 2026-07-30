import json
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

    alerta_sensivel = db.Column(db.Boolean, nullable=False, default=False)
    alerta_sensivel_tipo = db.Column(db.String(50), nullable=True)
    alerta_sensivel_nivel = db.Column(db.String(20), nullable=True)
    alerta_sensivel_motivos = db.Column(db.Text, nullable=True)
    acao_tomada = db.Column(db.Text, nullable=True)
    acompanhamento = db.Column(db.Text, nullable=True)
    data_acompanhamento = db.Column(db.Date, nullable=True)
    status_acompanhamento = db.Column(db.String(30), nullable=False, default='nao_aplicavel')

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

        motivos_sensiveis = []
        if self.alerta_sensivel_motivos:
            try:
                motivos_sensiveis = json.loads(self.alerta_sensivel_motivos)
            except (TypeError, ValueError):
                motivos_sensiveis = [self.alerta_sensivel_motivos]

        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': aluno_nome,
            'aluno_matricula': aluno_matricula,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'data': self.data.isoformat() if self.data else None,
            'data_ocorrencia': self.data_ocorrencia.isoformat() if self.data_ocorrencia else None,
            'alerta_sensivel': bool(self.alerta_sensivel),
            'alerta_sensivel_tipo': self.alerta_sensivel_tipo,
            'alerta_sensivel_nivel': self.alerta_sensivel_nivel,
            'alerta_sensivel_motivos': motivos_sensiveis,
            'acao_tomada': self.acao_tomada,
            'acompanhamento': self.acompanhamento,
            'data_acompanhamento': self.data_acompanhamento.isoformat() if self.data_acompanhamento else None,
            'status_acompanhamento': self.status_acompanhamento,
            'turma_id': self.turma_id,
            'turma_nome': self.turma.nome if self.turma else None
        }
