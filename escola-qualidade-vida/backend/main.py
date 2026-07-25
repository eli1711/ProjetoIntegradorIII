import os
import time
import logging
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash

from app import create_app, db


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "sim"}


app = create_app()
debug_enabled = _env_bool("DEBUG", False)

logging.basicConfig(
    level=logging.DEBUG if debug_enabled else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if debug_enabled else logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
app.logger.addHandler(console_handler)


def retry_on_failure(retries=5, backoff_factor=2):
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
                    app.logger.warning(
                        "Erro ao conectar ao banco de dados. Tentativa %s/%s. "
                        "Nova tentativa em %s segundos. Detalhes: %s",
                        attempt,
                        retries,
                        backoff_time,
                        e,
                    )
                    time.sleep(backoff_time)
            raise RuntimeError(f"Falha ao conectar ao banco de dados apos {retries} tentativas.")
        return wrapper
    return decorator


@retry_on_failure(retries=5, backoff_factor=2)
def wait_for_db():
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    engine = create_engine(db_uri)
    with engine.connect():
        app.logger.info("Conexao bem-sucedida com o banco de dados.")


def create_first_user():
    if not _env_bool("CREATE_DEFAULT_ADMIN", False):
        app.logger.info("Criacao automatica de admin desativada.")
        return

    from app.models import Usuario

    if Usuario.query.first() is not None:
        app.logger.info("Ja existem usuarios no sistema.")
        return

    email = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@admin.com")
    password = os.environ.get("DEFAULT_ADMIN_PASSWORD")
    if not password:
        app.logger.warning("DEFAULT_ADMIN_PASSWORD nao definido; admin inicial nao foi criado.")
        return

    primeiro_usuario = Usuario(
        nome=os.environ.get("DEFAULT_ADMIN_NAME", "Administrador"),
        email=email,
        senha=generate_password_hash(password),
        cargo="administrador",
    )

    db.session.add(primeiro_usuario)
    db.session.commit()
    app.logger.info("Primeiro usuario administrador criado: %s", email)


with app.app_context():
    try:
        wait_for_db()
        db.create_all()
        app.logger.info("Tabelas verificadas/criadas com sucesso.")
        create_first_user()
    except Exception as e:
        app.logger.error("Erro ao preparar o banco de dados: %s", e)
        raise


if __name__ == "__main__":
    app.run(debug=debug_enabled, host="0.0.0.0", port=5000)
