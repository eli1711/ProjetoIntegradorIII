from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.database import Base

class Ocorrencia(Base):
    __tablename__ = "ocorrencia"

    id_ocorrencia = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("aluno.id_aluno"))
    tipo = Column(String(50), nullable=False)
    descricao = Column(Text, nullable=False)
    data = Column(DateTime, default=datetime.utcnow)

    aluno = relationship("Aluno", back_populates="ocorrencias")

    def to_dict(self):
        return {
            "id": self.id_ocorrencia,
            "aluno_id": self.aluno_id,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "data": self.data.isoformat()
        }
