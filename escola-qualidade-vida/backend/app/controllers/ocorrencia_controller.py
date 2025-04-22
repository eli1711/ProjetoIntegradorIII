from fastapi import APIRouter
from app import db


router = APIRouter()

@router.get("/")
def listar_ocorrencias():
    return {"mensagem": "Lista de ocorrências"}
