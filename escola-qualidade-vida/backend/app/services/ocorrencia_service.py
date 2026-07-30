from app.models.ocorrencia import Ocorrencia


def listar_ocorrencias():
    ocorrencias = Ocorrencia.query.order_by(Ocorrencia.data.desc()).all()
    return [ocorrencia.to_dict() for ocorrencia in ocorrencias]
