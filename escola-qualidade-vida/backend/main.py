import os
import time
from app import create_app, db
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine

app = create_app()

def wait_for_db():
    """Espera até que o banco de dados esteja disponível."""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(db_uri)
    attempt = 0
    while True:
        try:
            with engine.connect():
                print("Conexão bem-sucedida com o banco de dados!")
                break
        except OperationalError:
            attempt += 1
            backoff_time = 2 ** attempt
            print(f"Banco de dados não disponível, tentando novamente em {backoff_time} segundos...")
            time.sleep(backoff_time)

# Aguarda disponibilidade do DB e cria tabelas
with app.app_context():
    wait_for_db()
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
