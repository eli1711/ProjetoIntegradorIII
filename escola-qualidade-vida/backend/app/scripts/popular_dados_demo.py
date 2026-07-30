from datetime import date, datetime, timedelta

from sqlalchemy import func

from app import create_app
from app.extensions import db
from app.models.aluno import Aluno, only_digits
from app.models.curso import Curso
from app.models.ocorrencia import Ocorrencia
from app.models.turma import Turma


COURSES = [
    "Informatica Basica",
    "Mecanica Industrial",
    "Eletricista Instalador",
    "Assistente Administrativo",
]

TURMAS = [
    ("INF-2026-A", "Informatica Basica", "1", date(2026, 2, 3), None),
    ("INF-2026-B", "Informatica Basica", "2", date(2026, 7, 20), None),
    ("MEC-2026-A", "Mecanica Industrial", "1", date(2026, 2, 3), None),
    ("ELE-2026-A", "Eletricista Instalador", "1", date(2026, 2, 3), None),
    ("ADM-2026-A", "Assistente Administrativo", "2", date(2026, 7, 20), None),
]

STUDENTS = [
    ("90000000001", "DEMO-2026-001", "Ana Clara", "Santos", 16, "INF-2026-A", "SESI", True),
    ("90000000002", "DEMO-2026-002", "Bruno", "Oliveira", 17, "INF-2026-A", "SEDUC", False),
    ("90000000003", "DEMO-2026-003", "Camila", "Ribeiro", 18, "INF-2026-B", "Nenhuma", False),
    ("90000000004", "DEMO-2026-004", "Diego", "Martins", 19, "INF-2026-B", "SESI", False),
    ("90000000005", "DEMO-2026-005", "Ester", "Lima", 15, "MEC-2026-A", "SEDUC", True),
    ("90000000006", "DEMO-2026-006", "Felipe", "Costa", 20, "MEC-2026-A", "Nenhuma", False),
    ("90000000007", "DEMO-2026-007", "Gabriela", "Almeida", 17, "MEC-2026-A", "SESI", False),
    ("90000000008", "DEMO-2026-008", "Heitor", "Mendes", 16, "ELE-2026-A", "SEDUC", False),
    ("90000000009", "DEMO-2026-009", "Isadora", "Ferreira", 18, "ELE-2026-A", "Nenhuma", False),
    ("90000000010", "DEMO-2026-010", "Joao Pedro", "Barbosa", 17, "ELE-2026-A", "SESI", False),
    ("90000000011", "DEMO-2026-011", "Karina", "Araujo", 19, "ADM-2026-A", "SEDUC", False),
    ("90000000012", "DEMO-2026-012", "Lucas", "Pereira", 18, "ADM-2026-A", "Nenhuma", True),
    ("90000000013", "DEMO-2026-013", "Mariana", "Gomes", 16, "ADM-2026-A", "SESI", False),
    ("90000000014", "DEMO-2026-014", "Nicolas", "Rocha", 20, "INF-2026-A", "Nenhuma", False),
    ("90000000015", "DEMO-2026-015", "Olivia", "Nunes", 17, "MEC-2026-A", "SEDUC", False),
]

OCCURRENCE_TEMPLATES = [
    (0, Ocorrencia.TIPO_ATRASO, "Chegou apos o inicio da primeira aula. Aluno orientado pela equipe escolar.", 18),
    (0, Ocorrencia.TIPO_APOIO_EDUCACIONAL, "Solicitou apoio para organizar rotina de estudos e entregas pendentes.", 11),
    (1, Ocorrencia.TIPO_ATENDIMENTO_PAIS, "Responsavel contatado para alinhamento sobre frequencia e acompanhamento.", 9),
    (2, Ocorrencia.TIPO_PROBLEMA_SAUDE, "Aluno relatou indisposicao durante o periodo. Encaminhado para acompanhamento.", 7),
    (3, Ocorrencia.TIPO_OUTROS, "Observacao registrada pela equipe de qualidade de vida.", 6),
    (4, Ocorrencia.TIPO_APOIO_PSICOLOGICO, "Atendimento inicial realizado para escuta e acolhimento.", 5),
    (5, Ocorrencia.TIPO_SAIDA_ANTECIPADA, "Saida antecipada autorizada mediante contato com responsavel.", 4),
    (6, Ocorrencia.TIPO_ATRASO, "Atraso recorrente identificado. Combinado novo acompanhamento semanal.", 3),
    (7, Ocorrencia.TIPO_ATENDIMENTO_EMPRESAS, "Contato com empresa parceira para alinhamento de frequencia.", 2),
    (8, Ocorrencia.TIPO_APOIO_EDUCACIONAL, "Encaminhado para reforco em conteudos praticos da unidade curricular.", 1),
    (9, Ocorrencia.TIPO_ATENDIMENTO_AAPM, "Orientacao sobre solicitacao de apoio institucional.", 14),
    (10, Ocorrencia.TIPO_VENDA_UNIFORME, "Registro de retirada de uniforme conforme solicitacao.", 13),
    (11, Ocorrencia.TIPO_OUTROS, "Aluno participou de orientacao coletiva sobre convivencia.", 12),
    (12, Ocorrencia.TIPO_APOIO_PSICOLOGICO, "Acompanhamento agendado apos relato de dificuldade emocional.", 10),
    (13, Ocorrencia.TIPO_ATRASO, "Atraso justificado por transporte. Registro mantido para acompanhamento.", 8),
    (14, Ocorrencia.TIPO_APOIO_EDUCACIONAL, "Plano de estudos revisado com foco em atividades pendentes.", 6),
    (2, Ocorrencia.TIPO_ATENDIMENTO_PAIS, "Familia orientada sobre canais de comunicacao com a escola.", 5),
    (5, Ocorrencia.TIPO_PROBLEMA_SAUDE, "Aluno liberado apos avaliacao e contato com responsavel.", 4),
    (8, Ocorrencia.TIPO_SAIDA_ANTECIPADA, "Saida antecipada por consulta medica previamente informada.", 3),
    (11, Ocorrencia.TIPO_ATENDIMENTO_EMPRESAS, "Empresa informada sobre ajuste no horario de aprendizagem.", 2),
]


def get_or_create_course(name):
    course = Curso.query.filter(func.lower(Curso.nome) == name.lower()).first()
    if course:
        return course, False

    course = Curso(nome=name)
    db.session.add(course)
    db.session.flush()
    return course, True


def get_or_create_turma(name, course, semester, start_date, end_date):
    turma = Turma.query.filter(
        Turma.curso_id == course.id,
        func.lower(Turma.nome) == name.lower(),
    ).first()
    if turma:
        turma.semestre = semester
        turma.data_inicio = start_date
        turma.data_fim = end_date
        return turma, False

    turma = Turma(
        nome=name,
        curso_id=course.id,
        semestre=semester,
        data_inicio=start_date,
        data_fim=end_date,
    )
    db.session.add(turma)
    db.session.flush()
    return turma, True


def upsert_student(student, turmas_by_name):
    cpf, matricula, first_name, last_name, age, turma_name, school, pcd = student
    turma = turmas_by_name[turma_name]
    course = turma.curso
    birth_date = date.today().replace(year=date.today().year - age)

    aluno = Aluno.query.filter_by(cpf=only_digits(cpf)).first()
    created = False
    if not aluno:
        aluno = Aluno(cpf=only_digits(cpf), matricula=matricula)
        created = True

    aluno.nome = first_name
    aluno.sobrenome = last_name
    aluno.nome_completo = f"{first_name} {last_name}"
    aluno.cidade = "Araraquara"
    aluno.bairro = "Centro"
    aluno.rua = f"Rua Demo, {100 + int(matricula[-3:])}"
    aluno.idade = age
    aluno.empregado = "sim" if age >= 18 else "nao"
    aluno.telefone = f"1699{int(matricula[-3:]):07d}"[-11:]
    aluno.data_nascimento = birth_date
    aluno.linha_atendimento = "CAI"
    aluno.escola_integrada = school
    aluno.curso = course.nome
    aluno.turma = turma.nome
    aluno.curso_id = course.id
    aluno.turma_id = turma.id
    aluno.mora_com_quem = "Familia"
    aluno.sobre_aluno = "Registro de demonstracao para testes do sistema."
    aluno.pessoa_com_deficiencia = pcd
    aluno.outras_informacoes = "Dados ficticios gerados para ambiente de desenvolvimento."
    aluno.normalize()

    db.session.add(aluno)
    db.session.flush()
    return aluno, created


def create_occurrence_if_needed(aluno, tipo, descricao, days_ago):
    event_date = date.today() - timedelta(days=days_ago)
    exists = Ocorrencia.query.filter_by(
        aluno_id=aluno.id,
        tipo=tipo,
        descricao=descricao,
        data_ocorrencia=event_date,
    ).first()
    if exists:
        return False

    occurrence = Ocorrencia(
        aluno_id=aluno.id,
        turma_id=aluno.turma_id,
        tipo=tipo,
        descricao=descricao,
        data_ocorrencia=event_date,
        data=datetime.utcnow() - timedelta(days=days_ago),
    )
    db.session.add(occurrence)
    return True


def popular():
    created_courses = 0
    created_turmas = 0
    created_students = 0
    created_occurrences = 0

    courses_by_name = {}
    for name in COURSES:
        course, created = get_or_create_course(name)
        courses_by_name[name] = course
        created_courses += int(created)

    turmas_by_name = {}
    for turma_name, course_name, semester, start_date, end_date in TURMAS:
        turma, created = get_or_create_turma(turma_name, courses_by_name[course_name], semester, start_date, end_date)
        turmas_by_name[turma_name] = turma
        created_turmas += int(created)

    students = []
    for student in STUDENTS:
        aluno, created = upsert_student(student, turmas_by_name)
        students.append(aluno)
        created_students += int(created)

    for student_index, tipo, descricao, days_ago in OCCURRENCE_TEMPLATES:
        created_occurrences += int(create_occurrence_if_needed(students[student_index], tipo, descricao, days_ago))

    db.session.commit()

    return {
        "created_courses": created_courses,
        "created_turmas": created_turmas,
        "created_students": created_students,
        "created_occurrences": created_occurrences,
        "total_courses": Curso.query.count(),
        "total_turmas": Turma.query.count(),
        "total_students": Aluno.query.count(),
        "total_occurrences": Ocorrencia.query.count(),
    }


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        result = popular()
        print(
            "Dados demo populados: "
            f"cursos_criados={result['created_courses']} "
            f"turmas_criadas={result['created_turmas']} "
            f"alunos_criados={result['created_students']} "
            f"ocorrencias_criadas={result['created_occurrences']} "
            f"totais=(cursos={result['total_courses']}, "
            f"turmas={result['total_turmas']}, "
            f"alunos={result['total_students']}, "
            f"ocorrencias={result['total_occurrences']})"
        )
