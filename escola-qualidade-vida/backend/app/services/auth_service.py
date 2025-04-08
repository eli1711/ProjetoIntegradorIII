# app/services/auth_service.py
from app.models.usuario import Usuario
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario and check_password_hash(usuario.senha, senha):
        return usuario
    return None