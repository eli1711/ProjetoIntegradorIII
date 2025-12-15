#shermas/aluno.py
from pydantic import BaseModel
from enum import Enum

class Periodo(str, Enum):
    MANHA = "manhã"
    TARDE = "tarde"
    NOITE = "noite"

class AlunoCreate(BaseModel):
    nome: str
    turma_id: int
    curso_id: int
    periodo: Periodo
    imagem: str = None
    nome_responsavel: str
    telefone_responsavel: str = None
    celular_responsavel: str
