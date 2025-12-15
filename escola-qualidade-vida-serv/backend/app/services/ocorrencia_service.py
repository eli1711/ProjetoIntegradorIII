from app.models.ocorrencia import Ocorrencia

def listar_ocorrencias():
    ocorrencias = Ocorrencia.query.all()
    return [
        {
            "id": o.id,
            "tipo": o.tipo,
            "descricao": o.descricao,
            "aluno_id": o.aluno_id,
            "usuario_id": o.usuario_id
        }
        for o in ocorrencias
    ]
