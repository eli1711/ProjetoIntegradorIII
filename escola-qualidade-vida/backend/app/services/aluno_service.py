from app.extensions import db
from app.models.aluno import Aluno, only_digits


def listar_alunos(limit=100):
    alunos = Aluno.query.order_by(Aluno.id.desc()).limit(limit).all()
    return [
        {
            "id": aluno.id,
            "nome": aluno.nome_completo or f"{aluno.nome} {aluno.sobrenome}".strip(),
            "cpf": aluno.cpf,
            "matricula": aluno.matricula,
        }
        for aluno in alunos
    ]


def cadastrar_aluno(data):
    cpf = only_digits(data.get("cpf"))
    if not cpf or len(cpf) != 11:
        raise ValueError("CPF invalido.")

    aluno = Aluno(
        cpf=cpf,
        matricula=data["matricula"],
        nome=data["nome"],
        sobrenome=data.get("sobrenome") or "",
        nome_completo=data.get("nome_completo") or f"{data['nome']} {data.get('sobrenome') or ''}".strip(),
        cidade=data["cidade"],
        bairro=data["bairro"],
        rua=data["rua"],
        idade=int(data["idade"]),
        empregado=data.get("empregado", "nao"),
        linha_atendimento=data.get("linha_atendimento", "CAI"),
        escola_integrada=data.get("escola_integrada", "Nenhuma"),
        curso=data.get("curso"),
        turma=data.get("turma"),
    )
    aluno.normalize()
    db.session.add(aluno)
    db.session.commit()
    return aluno
