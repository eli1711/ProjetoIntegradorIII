import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app import create_app
from app.services.ia_aluno_service import detectar_alertas_ocorrencia, _contexts_for_external_ai


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_expected_routes_are_registered():
    app = create_app()
    routes = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/auth/login" in routes
    assert "/cadastro/alunos" in routes
    assert "/cursos/" in routes
    assert "/turmas/" in routes
    assert "/alunos/buscar" in routes
    assert "/alunos/<int:aluno_id>" in routes
    assert "/alunos/<int:aluno_id>/foto" in routes
    assert "/ocorrencias/" in routes
    assert "/ocorrencias/listar" in routes
    assert "/ocorrencias/sensiveis" in routes
    assert "/ocorrencias/sensiveis/sincronizar" in routes
    assert "/ia/alunos/analise" in routes


def test_debug_routes_are_disabled_by_default():
    app = create_app()
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/debug/users" not in routes


def test_public_auth_test_routes_are_not_registered():
    app = create_app()
    routes = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/auth/test" not in routes
    assert "/auth/recuperar_senha_test" not in routes
    assert "/auth/test_redefinir" not in routes


def test_uploads_are_served_only_through_authenticated_route():
    app = create_app()
    routes = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/uploads/<path:filename>" not in routes
    assert "/files/uploads/<path:filename>" in routes


def test_sensitive_occurrence_sync_is_explicit_post_route():
    app = create_app()
    methods_by_route = {rule.rule: rule.methods for rule in app.url_map.iter_rules()}

    assert "GET" in methods_by_route["/ocorrencias/sensiveis"]
    assert "POST" not in methods_by_route["/ocorrencias/sensiveis"]
    assert "POST" in methods_by_route["/ocorrencias/sensiveis/sincronizar"]


def test_startup_does_not_create_or_alter_schema():
    source = (BACKEND_ROOT / "main.py").read_text(encoding="utf-8", errors="ignore")

    assert "db.create_all" not in source
    assert "ALTER TABLE" not in source


def test_password_reset_tokens_are_not_logged():
    source = (BACKEND_ROOT / "app" / "routers" / "auth_routes.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    assert "ALLOW_PASSWORD_RESET_TOKEN_LOG" not in source
    assert "token=%s" not in source


def test_external_ai_context_redacts_personal_data_by_default(monkeypatch):
    monkeypatch.delenv("OPENAI_SEND_PERSONAL_DATA", raising=False)

    redacted = _contexts_for_external_ai([
        {
            "aluno_id": 7,
            "nome": "Nome Real",
            "curso": "Curso",
            "turma": "Turma",
            "ocorrencias": [
                {
                    "tipo": "Outros",
                    "descricao": "Texto sensivel da ocorrencia",
                    "data_ocorrencia": "2026-08-05",
                }
            ],
        }
    ])

    assert redacted[0]["nome"] == "Aluno 7"
    assert redacted[0]["ocorrencias"][0]["descricao"] == "[omitida por privacidade]"


def test_controlled_medication_occurrence_triggers_sensitive_alert():
    alerta = detectar_alertas_ocorrencia(
        "Outros",
        "aluno foi pego fazendo o uso de remedios controlados no banheiro",
    )

    assert alerta["ativo"] is True
    assert alerta["tipo"] == "seguranca"
    assert alerta["nivel"] == "critico"
    assert "Uso indevido de medicamentos controlados" in alerta["motivos"]
