import os

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.usuario import Usuario


def atualizar_senha():
    email = (os.environ.get("TARGET_EMAIL") or "").strip().lower()
    nova_senha = os.environ.get("NEW_PASSWORD") or ""

    if not email or not nova_senha:
        raise RuntimeError("Defina TARGET_EMAIL e NEW_PASSWORD antes de executar este script.")
    if len(nova_senha) < 8:
        raise RuntimeError("NEW_PASSWORD deve ter pelo menos 8 caracteres.")

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        print("Usuario nao encontrado.")
        return

    usuario.senha = generate_password_hash(nova_senha)
    usuario.token_recuperacao = None
    usuario.token_expiracao = None
    db.session.commit()
    print(f"Senha atualizada com sucesso para {email}.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        atualizar_senha()
