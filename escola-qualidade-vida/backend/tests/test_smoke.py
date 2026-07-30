import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app import create_app
from app.services.ia_aluno_service import detectar_alertas_ocorrencia


def test_expected_routes_are_registered():
    app = create_app()
    routes = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/auth/login" in routes
    assert "/cursos/" in routes
    assert "/turmas/" in routes
    assert "/alunos/buscar" in routes
    assert "/alunos/<int:aluno_id>" in routes
    assert "/alunos/<int:aluno_id>/foto" in routes
    assert "/ocorrencias/" in routes
    assert "/ocorrencias/listar" in routes
    assert "/ocorrencias/sensiveis" in routes
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


def test_controlled_medication_occurrence_triggers_sensitive_alert():
    alerta = detectar_alertas_ocorrencia(
        "Outros",
        "aluno foi pego fazendo o uso de remedios controlados no banheiro",
    )

    assert alerta["ativo"] is True
    assert alerta["tipo"] == "seguranca"
    assert alerta["nivel"] == "critico"
    assert "Uso indevido de medicamentos controlados" in alerta["motivos"]
