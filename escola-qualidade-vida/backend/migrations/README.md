# Migrações do banco

Este projeto está preparado para usar Flask-Migrate.

Fluxo recomendado dentro do container/backend:

```bash
flask db init
flask db migrate -m "estrutura inicial"
flask db upgrade
```

Depois que a pasta `migrations/` for criada pelo comando acima, versionar essa pasta no Git.
