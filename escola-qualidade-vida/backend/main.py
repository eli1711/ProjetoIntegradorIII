import os
import time
import logging
from functools import wraps

from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

from app import create_app, db

app = create_app()

# -------------------------
# LOGS
# -------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Evita adicionar handler duplicado
if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    app.logger.addHandler(console_handler)

app.logger.setLevel(logging.DEBUG)

# -------------------------
# RETRY DB
# -------------------------
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
                    backoff_time = backoff_factor**attempt
                    app.logger.warning(
                        f"Erro ao conectar ao banco. Tentativa {attempt}/{retries}. "
                        f"Retry em {backoff_time}s. Detalhes: {e}"
                    )
                    time.sleep(backoff_time)
            raise Exception(f"Falha ao conectar ao banco após {retries} tentativas.")
        return wrapper
    return decorator


@retry_on_failure(retries=10, backoff_factor=1)
def wait_for_db():
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not db_uri:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI não configurada no create_app().")

    engine = create_engine(db_uri, pool_pre_ping=True)
    with engine.connect():
        app.logger.info("✅ Conexão com o banco OK!")


# -------------------------
# IMPORTA MODELS (registra mappers)
# -------------------------
def import_all_models():
    """
    IMPORTANTE:
    Isso evita problemas do create_all() não enxergar tabelas por falta de import.
    Ajuste caso os nomes dos arquivos sejam diferentes.
    """
    from app.models.aluno import Aluno  # noqa: F401
    from app.models.responsavel import Responsavel  # noqa: F401
    from app.models.empresa import Empresa  # noqa: F401
    from app.models.curso import Curso  # noqa: F401
    from app.models.turma import Turma  # noqa: F401
    from app.models.usuario import Usuario  # noqa: F401


# -------------------------
# RESET DO SCHEMA (DEV ONLY)
# -------------------------
def reset_public_schema():
    """
    Apaga tudo do schema public e recria.
    Use apenas em DEV.
    """
    app.logger.warning("⚠️ RESET DO BANCO: apagando schema public (DEV ONLY)")
    db.session.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
    db.session.execute(text("CREATE SCHEMA public;"))
    db.session.commit()


# -------------------------
# CRIA ADMIN INICIAL
# -------------------------
def create_first_user():
    try:
        from app.models.usuario import Usuario

        if Usuario.query.first() is None:
            primeiro_usuario = Usuario(
                nome="Administrador",
                email="admin@admin.com",
                senha=generate_password_hash("admin123"),
                cargo="administrador",
            )
            db.session.add(primeiro_usuario)
            db.session.commit()
            app.logger.info("✅ Admin criado: admin@admin.com / admin123")
        else:
            app.logger.info("ℹ️ Já existem usuários no sistema.")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"❌ Erro ao criar primeiro usuário: {e}")


# -------------------------
# BOOTSTRAP
# -------------------------
with app.app_context():
    wait_for_db()

    # Ative via docker-compose:
    # RESET_DB=1
    if os.getenv("RESET_DB", "0") == "1":
        reset_public_schema()

    import_all_models()

    try:
        db.create_all()
        app.logger.info("✅ Tabelas criadas via SQLAlchemy create_all()!")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise

    create_first_user()


if __name__ == "__main__":
    # Em container, debug geralmente deve ser False.
    # Se você quiser controlar por env:
    debug = os.getenv("DEBUG", "False").lower() in ("1", "true", "t", "yes", "y", "sim")
    app.run(debug=debug, host="0.0.0.0", port=5000)
