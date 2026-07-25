import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.permission_service import auth_required


upload_bp = Blueprint("upload", __name__)
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".csv", ".pdf"}


@upload_bp.route("/upload", methods=["POST"])
@auth_required()
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nome de arquivo vazio"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        return jsonify({"error": "Tipo de arquivo nao permitido"}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    upload_path = os.path.join(upload_folder, filename)
    file.save(upload_path)

    return jsonify({
        "message": "Arquivo salvo com sucesso",
        "filename": filename,
        "url": f"/uploads/{filename}",
    }), 200
