import os

from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def salvar_foto(foto_file, aluno_nome, destino=None):
    upload_dir = destino or current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(foto_file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise ValueError("Extensao de imagem invalida.")

    base = secure_filename((aluno_nome or "aluno").lower()) or "aluno"
    filename = f"{base}{ext}"
    caminho = os.path.join(upload_dir, filename)

    contador = 1
    while os.path.exists(caminho):
        filename = f"{base}_{contador}{ext}"
        caminho = os.path.join(upload_dir, filename)
        contador += 1

    foto_file.save(caminho)
    return filename
