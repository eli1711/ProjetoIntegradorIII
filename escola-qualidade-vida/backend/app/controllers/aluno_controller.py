from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.models.aluno import Aluno
from app import db

router = APIRouter()

@router.get("/consultar")
async def consultar_alunos():
    alunos = db.query(Aluno).all()
    return {"alunos": alunos}
