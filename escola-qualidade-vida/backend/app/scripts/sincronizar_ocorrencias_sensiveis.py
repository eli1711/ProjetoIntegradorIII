from app import create_app
from app.routers.ocorrencia_routes import _sync_ocorrencias_sensiveis_existentes


def main():
    app = create_app()
    with app.app_context():
        updated = _sync_ocorrencias_sensiveis_existentes()
        print(f"Ocorrencias sensiveis sincronizadas: {updated}")


if __name__ == "__main__":
    main()
