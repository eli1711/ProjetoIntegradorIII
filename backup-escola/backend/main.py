import os
import time
from flask import Flask
from app import create_app, db
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
import logging
from functools import wraps

# Configuração do Flask
app = create_app()

# Configuração de logs
log_file = 'app.log'
logging.basicConfig(level=logging.DEBUG,  # Captura DEBUG, INFO, WARNING, ERROR, CRITICAL
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Adicionando um Handler para também exibir logs no console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)

def retry_on_failure(retries=5, backoff_factor=2):
    """
    Função decoradora que aplica uma política de retry (tentativas) em caso de falhas.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    attempt += 1
                    backoff_time = backoff_factor ** attempt
                    app.logger.warning(f"Erro ao conectar ao banco de dados. Tentativa {attempt}/{retries}. "
                                       f"Voltando a tentar em {backoff_time} segundos. Detalhes: {e}")
                    time.sleep(backoff_time)
            raise Exception(f"Falha ao conectar ao banco de dados após {retries} tentativas.")
        return wrapper
    return decorator

# Função para conectar ao banco de dados com retry
@retry_on_failure(retries=5, backoff_factor=2)
def wait_for_db():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(db_uri)
    with engine.connect():
        app.logger.info("Conexão bem-sucedida com o banco de dados!")

with app.app_context():
    try:
        wait_for_db()  # Espera pela conexão com o banco de dados
        db.create_all()  # Cria as tabelas do banco
        app.logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        app.logger.error(f"Erro ao criar as tabelas do banco de dados: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
