from flask import Blueprint

# Definindo o Blueprint para as ocorrências
ocorrencia_bp = Blueprint('ocorrencias', __name__)

@ocorrencia_bp.route('/listar', methods=['GET'])
def listar_ocorrencias():
    # Lógica para listar as ocorrências
    return "Lista de ocorrências"
