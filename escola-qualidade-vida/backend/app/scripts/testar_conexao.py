from sqlalchemy import create_engine

from app.config import SQLALCHEMY_DATABASE_URI


engine = create_engine(SQLALCHEMY_DATABASE_URI)

try:
    with engine.connect():
        print("Conexao com o PostgreSQL bem-sucedida.")
except Exception as e:
    print(f"Erro ao conectar ao PostgreSQL: {e}")
