import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Banco de Dados
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "escola_db")

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuração de Uploads
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/uploads')

# Allowed file types (opcional, você pode usar ou não)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
