import os
from flask_sqlalchemy import SQLAlchemy

# Inicializar o objeto db do SQLAlchemy
db = SQLAlchemy()

# Construa a URL do banco de dados com variáveis de ambiente
DATABASE_URL = (
    f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@"
    f"{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)

# Classe Base para todos os modelos SQLAlchemy
class Base(db.Model):
    __abstract__ = True  # Esta classe não será mapeada diretamente para uma tabela
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Aqui você pode adicionar outros métodos ou configurações que deseja aplicar a todos os modelos
