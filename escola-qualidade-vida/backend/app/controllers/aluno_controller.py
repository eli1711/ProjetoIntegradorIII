from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_alunos():
    return {"mensagem": "Lista de alunos"}
