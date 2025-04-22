from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.utils.database import Base

class Curso(Base):
    __tablename__ = "curso"

    id_curso = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)

    alunos = relationship("Aluno", back_populates="curso")
