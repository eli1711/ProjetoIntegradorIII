from pydantic import BaseModel

class OcorrenciaCreate(BaseModel):
    aluno_id: int
    tipo: str
    descricao: str
    usuario_id: int
