from app.models.ocorrencia import Ocorrencia
from app.utils.database import get_db_session

def listar_ocorrencias():
    session = get_db_session()
    ocorrencias = session.query(Ocorrencia).all()
    session.close()
    return ocorrencias
