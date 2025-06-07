import os
from werkzeug.utils import secure_filename

def salvar_foto(foto_file, aluno_nome, destino='/backend/app/uploads'):
    caminho_absoluto = os.path.join(os.path.abspath(os.path.dirname(__file__)), destino)

    # Verificar se o diretório de uploads existe, senão, criar
    if not os.path.exists(caminho_absoluto):
        os.makedirs(caminho_absoluto)

    # Obter a extensão da imagem
    ext = os.path.splitext(foto_file.filename)[1].lower()

    # Criar o nome do arquivo com o nome do aluno
    aluno_nome_securizado = secure_filename(aluno_nome.lower())  # Convertendo o nome para minúsculas
    filename = f"{aluno_nome_securizado}{ext}"

    caminho = os.path.join(caminho_absoluto, filename)

    # Verificar se já existe um arquivo com esse nome e adicionar um contador caso exista
    contador = 1
    while os.path.exists(caminho):
        filename = f"{aluno_nome_securizado}_{contador}{ext}"
        caminho = os.path.join(caminho_absoluto, filename)
        contador += 1

    # Salvar o arquivo
    foto_file.save(caminho)
    return filename
