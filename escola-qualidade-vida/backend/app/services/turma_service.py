from datetime import date, datetime

from app.extensions import db
from app.models.turma import Turma


def listar_turmas():
    turmas = Turma.query.order_by(Turma.id.desc()).all()
    return [
        {
            "id": turma.id,
            "nome": turma.nome,
            "curso_id": turma.curso_id,
            "semestre": turma.semestre,
            "data_inicio": turma.data_inicio.isoformat() if turma.data_inicio else None,
            "data_fim": turma.data_fim.isoformat() if turma.data_fim else None,
        }
        for turma in turmas
    ]


def criar_turma(dados):
    if not dados.get("curso_id"):
        raise ValueError("curso_id e obrigatorio.")

    def parse_date(value):
        if not value:
            return None
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    turma = Turma(
        nome=dados["nome"],
        curso_id=int(dados["curso_id"]),
        semestre=str(dados.get("semestre") or "1"),
        data_inicio=parse_date(dados.get("data_inicio")) or date.today(),
        data_fim=parse_date(dados.get("data_fim")),
    )
    db.session.add(turma)
    db.session.commit()
    return {"id": turma.id, "nome": turma.nome}
