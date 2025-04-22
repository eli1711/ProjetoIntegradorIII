from fastapi import APIRouter
from app import db

router = APIRouter()

@router.get("/")
def listar_alunos():
    return {"mensagem": "Lista de alunos"}
