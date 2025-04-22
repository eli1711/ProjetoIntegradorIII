from app import create_app, db
from sqlalchemy import text

app = create_app()

# Teste de Conexão com o banco de dados
with app.app_context():
    try:
        # Executa a consulta SQL
        result = db.session.execute(text("SELECT 1"))
        print("✅ Conexão bem-sucedida com o MySQL!")
    except Exception as e:
        print(f"❌ Erro ao conectar com o MySQL: {e}")
