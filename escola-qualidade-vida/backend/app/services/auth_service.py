from app.models.usuario import Usuario

def verificar_usuario(email):
    return Usuario.query.filter_by(email=email).first()
