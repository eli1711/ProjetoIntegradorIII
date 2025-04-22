from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.utils.database import Base

class Turma(Base):
    __tablename__ = "turma"

    id_turma = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)

    alunos = relationship("Aluno", back_populates="turma")
