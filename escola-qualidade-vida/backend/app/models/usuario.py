from sqlalchemy import Column, Integer, String, Enum
from app.utils.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    tipo_usuario = Column(Enum("admin", "professor", "coordenador", name="tipo_usuario_enum"), nullable=False, default="professor")
