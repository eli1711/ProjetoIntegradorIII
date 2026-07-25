import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app import create_app


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


def test_sensitive_debug_routes_require_authentication():
    app = create_app()

    with app.test_client() as client:
        response = client.get("/routes")

    assert response.status_code in {401, 422}
