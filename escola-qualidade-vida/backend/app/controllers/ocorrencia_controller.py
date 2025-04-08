from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_ocorrencias():
    return {"mensagem": "Lista de ocorrências"}
