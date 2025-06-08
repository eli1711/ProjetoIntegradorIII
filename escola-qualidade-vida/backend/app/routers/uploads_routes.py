# app/routers/upload_routes.py
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    # Secure filename to avoid unsafe characters
    filename = secure_filename(file.filename)
    
    # Caminho da pasta de uploads no container (dentro de /backend/app/uploads/)
    upload_folder = os.path.join(current_app.root_path, 'backend', 'app', 'uploads')
    
    # Cria o diretório de uploads, se não existir
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Define o caminho completo para o arquivo de upload
    upload_path = os.path.join(upload_folder, filename)
    
    # Salva o arquivo no caminho configurado
    file.save(upload_path)
    
    # Retorna a resposta de sucesso com o nome do arquivo
    return jsonify({'message': 'Arquivo salvo com sucesso', 'filename': filename}), 200
