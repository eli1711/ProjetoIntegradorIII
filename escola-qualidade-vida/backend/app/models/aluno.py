from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.utils.database import Base

class Empregado(PyEnum):
    SIM = "sim"
    NAO = "no"

class Aluno(Base):
    __tablename__ = "aluno"

    id_aluno = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    sobrenome = Column(String(255), nullable=False)
    cidade = Column(String(255), nullable=False)
    bairro = Column(String(255), nullable=False)
    rua = Column(String(255), nullable=False)
    idade = Column(Integer, nullable=False)
    empregado = Column(Enum(Empregado), nullable=False)
    coma_com_quem = Column(String(255), nullable=True)
    comorbidade = Column(Text, nullable=True)
    foto = Column(LargeBinary, nullable=True)

    turma = relationship("Turma", back_populates="alunos")
    curso = relationship("Curso", back_populates="alunos")
    ocorrencias = relationship("Ocorrencia", back_populates="aluno")
