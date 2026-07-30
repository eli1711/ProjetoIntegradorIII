import os

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.usuario import Usuario


VALID_CARGOS = {"administrador", "coordenador", "analista"}


def criar_usuario():
    nome = (os.environ.get("ADMIN_NAME") or "").strip()
    email = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
    senha = os.environ.get("ADMIN_PASSWORD") or ""
    cargo = (os.environ.get("ADMIN_CARGO") or "administrador").strip()

    if not nome or not email or not senha:
        raise RuntimeError("Defina ADMIN_NAME, ADMIN_EMAIL e ADMIN_PASSWORD antes de executar este script.")
    if len(senha) < 8:
        raise RuntimeError("ADMIN_PASSWORD deve ter pelo menos 8 caracteres.")
    if cargo not in VALID_CARGOS:
        raise RuntimeError(f"ADMIN_CARGO invalido. Use um destes valores: {', '.join(sorted(VALID_CARGOS))}.")

    if Usuario.query.filter_by(email=email).first():
        print("Usuario ja existe.")
        return

    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        cargo=cargo,
    )
    db.session.add(novo_usuario)
    db.session.commit()
    print("Usuario criado com sucesso.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        criar_usuario()
