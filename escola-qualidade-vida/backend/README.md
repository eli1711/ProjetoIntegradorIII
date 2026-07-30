# Backend - Escola Qualidade de Vida

Backend Flask para cadastro de alunos, turmas, ocorrencias, dashboard, usuarios e autenticacao JWT.

## Ambiente

Crie um `.env` na raiz do projeto a partir de `.env.example` e defina, no minimo:

- `SECRET_KEY`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `FRONTEND_URL`

Variaveis uteis:

- `JWT_SECRET_KEY`: chave especifica para tokens JWT. Se ficar vazia, usa `SECRET_KEY`.
- `MAX_UPLOAD_MB`: limite global para uploads, em MB. Padrao: `10`.
- `CREATE_DEFAULT_ADMIN`: use `1` apenas em ambiente controlado.
- `DEFAULT_ADMIN_PASSWORD`: obrigatoria quando `CREATE_DEFAULT_ADMIN=1`.
- `ALLOW_PASSWORD_RESET_TOKEN_LOG`: mantenha `0`. Use `1` apenas em desenvolvimento local e temporario.
- `ENABLE_OPENAI_ANALYSIS`: use `1` para habilitar analise com OpenAI. Padrao: `0`, usando regras locais.
- `OPENAI_API_KEY`: chave da OpenAI usada pela analise quando habilitada.
- `OPENAI_MODEL`: modelo usado pela analise. Padrao: `gpt-4o-mini`.
- `OPENAI_TIMEOUT_SECONDS`: timeout da chamada externa. Padrao: `20`.

## Docker

Na raiz do projeto:

```bash
docker compose up --build
```

Frontend: `http://localhost:8080`

Backend: `http://localhost:5000`

## Usuarios administrativos

Prefira criar usuarios pela tela do sistema. Para script local, use:

```bash
ADMIN_NAME="Administrador" ADMIN_EMAIL="admin@example.com" ADMIN_PASSWORD="senha-segura" ADMIN_CARGO="administrador" python -m app.scripts.criar_usuario
```

No PowerShell:

```powershell
$env:ADMIN_NAME="Administrador"; $env:ADMIN_EMAIL="admin@example.com"; $env:ADMIN_PASSWORD="senha-segura"; $env:ADMIN_CARGO="administrador"; python -m app.scripts.criar_usuario
```

Para atualizar senha:

```bash
TARGET_EMAIL="admin@example.com" NEW_PASSWORD="nova-senha-segura" python -m app.scripts.atualiza_senha
```

No PowerShell:

```powershell
$env:TARGET_EMAIL="admin@example.com"; $env:NEW_PASSWORD="nova-senha-segura"; python -m app.scripts.atualiza_senha
```

## Banco de dados

O projeto ja inicializa `Flask-Migrate`. Para evolucoes de schema, use migracoes:

```bash
flask db migrate -m "descricao"
flask db upgrade
```

Evite alterar schema manualmente em producao.

## IA de acompanhamento

A rota `GET /ia/alunos/analise` analisa alunos e ocorrencias para sugerir acoes de acompanhamento. Ela exige permissao de dashboard e aceita `limit` para controlar a quantidade de alunos analisados.

Tambem existe `GET /ia/alunos/<id>/analise` para analisar um aluno especifico.

Por padrao, a analise roda em modo heuristico local. Para usar OpenAI, defina `ENABLE_OPENAI_ANALYSIS=1`, `OPENAI_API_KEY` e, opcionalmente, `OPENAI_MODEL`, depois reinicie o backend.
