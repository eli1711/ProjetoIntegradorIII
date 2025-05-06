from sqlalchemy import create_engine
from config import SQLALCHEMY_DATABASE_URI

# Testando a conexão com o banco
engine = create_engine(SQLALCHEMY_DATABASE_URI)

try:
    with engine.connect() as connection:
        print("Conexão com o MySQL bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar ao MySQL: {e}")
