from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.utils.database import Base

class Periodo(PyEnum):
    MANHA = "manhã"
    TARDE = "tarde"
    NOITE = "noite"

class Aluno(Base):
    __tablename__ = "aluno"

    id_aluno = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    turma_id = Column(Integer, ForeignKey("turma.id_turma"))
    curso_id = Column(Integer, ForeignKey("curso.id_curso"))
    periodo = Column(Enum(Periodo), nullable=False)
    imagem = Column(String(255))
    nome_responsavel = Column(String(100), nullable=False)
    telefone_responsavel = Column(String(20))
    celular_responsavel = Column(String(20), nullable=False)

    turma = relationship("Turma", back_populates="alunos")
    curso = relationship("Curso", back_populates="alunos")
    ocorrencias = relationship("Ocorrencia", back_populates="aluno")
