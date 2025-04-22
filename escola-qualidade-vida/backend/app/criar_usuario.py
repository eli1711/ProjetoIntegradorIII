# criar_usuario.py

from werkzeug.security import generate_password_hash
from app import db
from app.models.usuario import Usuario

def criar_usuario():
    nome = "Eli Mariano"
    email = "eli_mariano@yahoo.com"
    senha_plana = "123456"

    if Usuario.query.filter_by(email=email).first():
        print("⚠️ Usuário já existe.")
        return

    hash_senha = generate_password_hash(senha_plana)
    novo_usuario = Usuario(nome=nome, email=email, senha=hash_senha)

    db.session.add(novo_usuario)
    db.session.commit()
    print("✅ Usuário criado com sucesso!")

if __name__ == '__main__':
    criar_usuario()
