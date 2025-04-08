# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.services.auth_service import autenticar_usuario
from app.utils.database import get_db

router = APIRouter()

@router.post("/login")
def login(email: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, email, senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    return RedirectResponse(url="/principal.html", status_code=303)
