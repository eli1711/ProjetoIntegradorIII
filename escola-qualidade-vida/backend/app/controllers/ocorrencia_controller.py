from fastapi import APIRouter, HTTPException
from app.models.ocorrencia import Ocorrencia
from app.schemas.ocorrencia import OcorrenciaCreate
from app.models.aluno import Aluno
from app import db

router = APIRouter()

@router.post("/registrar", status_code=201)
async def registrar_ocorrencia(ocorrencia: OcorrenciaCreate):
    # Verifica se o aluno existe
    aluno = db.query(Aluno).filter_by(id_aluno=ocorrencia.aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado!")

    # Cria a nova ocorrência
    nova_ocorrencia = Ocorrencia(
        aluno_id=ocorrencia.aluno_id,
        tipo=ocorrencia.tipo,
        descricao=ocorrencia.descricao,
        usuario_id=ocorrencia.usuario_id
    )

    # Salva no banco de dados
    db.add(nova_ocorrencia)
    db.commit()
    db.refresh(nova_ocorrencia)

    return {"mensagem": "Ocorrência registrada com sucesso!", "ocorrencia": nova_ocorrencia}
