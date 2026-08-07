# Migracoes do banco

Esta pasta contem as migracoes versionadas do Flask-Migrate/Alembic.

Fluxo recomendado dentro do container/backend:

```bash
python -m flask --app app:create_app db migrate -m "descricao"
python -m flask --app app:create_app db upgrade
```

Nao use `flask db init` neste projeto: a estrutura de migrations ja esta versionada.
