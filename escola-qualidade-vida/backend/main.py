import os
import time
from flask import Flask
from app import create_app, db
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
import logging

# Configuração do Flask
app = create_app()

# Configuração de logs
log_file = 'app.log'
logging.basicConfig(filename=log_file,
                    level=logging.DEBUG,  # Captura DEBUG, INFO, WARNING, ERROR, CRITICAL
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def wait_for_db():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(db_uri)
    attempt = 0
    while True:
        try:
            with engine.connect():
                app.logger.info("Conexão bem-sucedida com o banco de dados!")
                break
        except OperationalError as e:
            attempt += 1
            backoff_time = 2 ** attempt
            app.logger.warning(f"Banco de dados não disponível, tentando novamente em {backoff_time} segundos...")
            app.logger.debug(f"Detalhes do erro: {e}")
            time.sleep(backoff_time)

with app.app_context():
    wait_for_db()  # Espera pela conexão com o banco de dados
    try:
        db.create_all()  # Cria as tabelas do banco
        app.logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        app.logger.error(f"Erro ao criar as tabelas do banco de dados: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
