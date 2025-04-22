from app import create_app
from app import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email_alvo = "admin@escola.com"
    nova_senha = "senha123"

    usuario = Usuario.query.filter_by(email=email_alvo).first()
    if usuario:
        usuario.senha = generate_password_hash(nova_senha)
        db.session.commit()
        print(f"Senha atualizada com sucesso para {email_alvo}")
    else:
        print("Usuário não encontrado.")
