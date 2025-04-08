import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "minha_chave_secreta")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
