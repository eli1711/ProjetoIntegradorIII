from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.usuario import Usuario
from app.utils.auth import verificar_senha
from app import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = db.query(Usuario).filter_by(email=form_data.username).first()
    if not usuario or not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Aqui, você pode adicionar lógica para gerar um token JWT se necessário
    return {"access_token": "token_aqui", "token_type": "bearer"}
