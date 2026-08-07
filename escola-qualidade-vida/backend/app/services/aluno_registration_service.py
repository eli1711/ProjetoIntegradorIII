import os
from datetime import date, datetime

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.aluno import Aluno, only_digits
from app.models.curso import Curso
from app.models.responsavel import Responsavel
from app.models.turma import Turma


class StudentRegistrationError(ValueError):
    def __init__(self, message, status_code=400, extra=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}

    def to_payload(self):
        return {"erro": self.message, **self.extra}


ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
LINHAS_ATENDIMENTO = {"CAI", "CT", "CST"}
ESCOLAS_INTEGRADAS = {"SESI", "SEDUC", "Nenhuma"}
EMPREGADO_VALUES = {"sim", "nao"}


def register_student_from_form(
    data,
    files=None,
    *,
    require_existing_course=True,
    validate_legacy_required=False,
):
    if validate_legacy_required:
        _validate_legacy_required_fields(data)

    cpf = only_digits(data.get("cpf"))
    if not cpf:
        raise StudentRegistrationError("CPF e obrigatorio")
    if len(cpf) != 11:
        raise StudentRegistrationError("CPF deve conter 11 digitos")
    if Aluno.query.filter_by(cpf=cpf).first():
        raise StudentRegistrationError("CPF ja cadastrado", 409)

    matricula = _none_if_empty(data.get("matricula"))
    if not matricula:
        raise StudentRegistrationError("Matricula e obrigatoria")
    if Aluno.query.filter_by(matricula=matricula).first():
        raise StudentRegistrationError("Matricula ja cadastrada", 409)

    nome_completo = _none_if_empty(data.get("nome_completo")) or ""
    nome = _none_if_empty(data.get("nome")) or ""
    sobrenome = _none_if_empty(data.get("sobrenome")) or ""
    if nome_completo and not nome:
        nome, sobrenome = _split_full_name(nome_completo)
    elif nome and sobrenome and not nome_completo:
        nome_completo = f"{nome} {sobrenome}".strip()

    if not nome:
        raise StudentRegistrationError("Nome do aluno e obrigatorio")

    data_nascimento = parse_date(_none_if_empty(data.get("data_nascimento")))
    idade = _resolve_age(data.get("idade"), data_nascimento)

    responsavel_obj = _build_responsavel_if_needed(data, idade)
    curso, turma = _resolve_course_and_class(
        data,
        require_existing_course=require_existing_course,
    )

    empregado = (_norm(data.get("empregado")) or "nao").lower()
    if empregado not in EMPREGADO_VALUES:
        raise StudentRegistrationError("empregado deve ser 'sim' ou 'nao'.")

    linha_atendimento = (_norm(data.get("linha_atendimento")) or "CAI").upper()
    if linha_atendimento not in LINHAS_ATENDIMENTO:
        raise StudentRegistrationError("linha_atendimento deve ser CAI, CT ou CST.")

    escola_integrada = _norm(data.get("escola_integrada") or "Nenhuma")
    if escola_integrada not in ESCOLAS_INTEGRADAS:
        raise StudentRegistrationError("escola_integrada deve ser SESI, SEDUC ou Nenhuma.")

    aluno = Aluno(
        cpf=cpf,
        matricula=matricula,
        nome=nome,
        sobrenome=sobrenome,
        nome_completo=nome_completo,
        nome_social=_none_if_empty(data.get("nome_social")),
        cidade=_first_non_empty(data, "cidade", "municipio") or "",
        bairro=_none_if_empty(data.get("bairro")) or "",
        rua=_first_non_empty(data, "rua", "endereco") or "",
        telefone=only_digits(_none_if_empty(data.get("telefone"))) or None,
        idade=idade,
        empregado=empregado,
        data_nascimento=data_nascimento,
        linha_atendimento=linha_atendimento,
        escola_integrada=escola_integrada,
        curso=curso.nome if curso else _none_if_empty(data.get("curso")),
        turma=turma.nome if turma else _none_if_empty(data.get("turma")),
        curso_id=curso.id if curso else None,
        turma_id=turma.id if turma else None,
        mora_com_quem=_none_if_empty(data.get("mora_com_quem")),
        sobre_aluno=_none_if_empty(data.get("sobre_aluno")),
        data_inicio_curso=parse_date(_none_if_empty(data.get("data_inicio_curso"))),
        empresa_contratante=_first_non_empty(
            data,
            "empresa_contratante",
            "empresa_aprendizagem",
        ),
        pessoa_com_deficiencia=str_to_bool(
            _first_non_empty(data, "pessoa_com_deficiencia", "pne")
        ),
        outras_informacoes=_first_non_empty(
            data,
            "outras_informacoes",
            "parceria_novo_ensino_medio",
        ),
        responsavel_id=responsavel_obj.id if responsavel_obj else None,
    )

    foto_file = files.get("foto") if files else None
    if foto_file and foto_file.filename:
        aluno.foto = save_student_photo(foto_file, nome_completo or nome)

    aluno.normalize()
    db.session.add(aluno)
    db.session.commit()
    return aluno


def parse_date(value):
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def str_to_bool(value):
    return str(value).strip().lower() in {"true", "1", "on", "t", "yes", "y", "sim"}


def save_student_photo(file_storage, desired_name_base):
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise StudentRegistrationError("Extensao de imagem invalida. Use JPG, PNG, GIF ou WEBP.")
    if file_storage.mimetype and file_storage.mimetype not in ALLOWED_IMAGE_MIMES:
        raise StudentRegistrationError("Tipo de imagem invalido. Use JPG, PNG, GIF ou WEBP.")

    base = secure_filename((desired_name_base or "aluno").lower()) or "aluno"
    filename = f"{base}{ext}"
    destination = os.path.join(upload_dir, filename)

    counter = 1
    while os.path.exists(destination):
        filename = f"{base}_{counter}{ext}"
        destination = os.path.join(upload_dir, filename)
        counter += 1

    file_storage.save(destination)
    return filename


def _validate_legacy_required_fields(data):
    required = [
        "matricula",
        "nome_completo",
        "cpf",
        "data_nascimento",
        "endereco",
        "cep",
        "bairro",
        "municipio",
        "curso",
        "tipo_curso",
        "turma",
    ]
    missing = [field for field in required if not _none_if_empty(data.get(field))]
    if missing:
        raise StudentRegistrationError(
            "Campos obrigatorios nao preenchidos",
            400,
            {"faltando": missing},
        )

    cep = only_digits(data.get("cep"))
    if not cep or len(cep) != 8:
        raise StudentRegistrationError("CEP invalido (informe 8 digitos)")

    cnpj = only_digits(data.get("cnpj_empresa"))
    empresa = _none_if_empty(data.get("empresa_aprendizagem"))
    if cnpj and len(cnpj) != 14:
        raise StudentRegistrationError("CNPJ invalido (informe 14 digitos)")
    if cnpj and not empresa:
        raise StudentRegistrationError("Informe o nome da empresa ao preencher CNPJ")
    if empresa and not cnpj:
        raise StudentRegistrationError("Informe o CNPJ ao preencher o nome da empresa")


def _resolve_age(raw_age, birth_date):
    raw_age = _none_if_empty(raw_age)
    if raw_age:
        try:
            return int(raw_age)
        except (TypeError, ValueError):
            raise StudentRegistrationError("idade invalida (inteiro).")

    calculated = _calc_age(birth_date)
    return calculated if calculated is not None else 18


def _calc_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def _build_responsavel_if_needed(data, age):
    if age >= 18:
        return None

    name = _none_if_empty(data.get("responsavel_nome_completo"))
    relation = _none_if_empty(data.get("responsavel_parentesco"))
    phone = only_digits(_none_if_empty(data.get("responsavel_telefone"))) or None
    if not (name and relation and phone):
        missing = [
            field
            for field in [
                "responsavel_nome_completo",
                "responsavel_parentesco",
                "responsavel_telefone",
            ]
            if not _none_if_empty(data.get(field))
        ]
        raise StudentRegistrationError(
            "Aluno menor de idade: campos do responsavel sao obrigatorios",
            400,
            {"faltando": missing},
        )

    cep = only_digits(_none_if_empty(data.get("responsavel_cep"))) or None
    if cep and len(cep) != 8:
        raise StudentRegistrationError("CEP do responsavel invalido (8 digitos)")

    responsavel = Responsavel(
        nome_completo=name,
        parentesco=relation,
        telefone=phone,
        endereco=_none_if_empty(data.get("responsavel_endereco")),
        cep=cep,
        bairro=_none_if_empty(data.get("responsavel_bairro")),
        municipio=_first_non_empty(data, "responsavel_cidade", "responsavel_municipio"),
    )
    db.session.add(responsavel)
    db.session.flush()
    return responsavel


def _resolve_course_and_class(data, *, require_existing_course):
    course_id = _none_if_empty(data.get("curso_id"))
    class_id = _none_if_empty(data.get("turma_id"))
    course_name = _none_if_empty(data.get("curso"))
    class_name = _none_if_empty(data.get("turma"))

    if require_existing_course:
        course = _resolve_existing_course(course_id, course_name)
        turma = _resolve_existing_turma(class_id, class_name, course)
        return course, turma

    course = _resolve_course_for_legacy_form(course_id, course_name)
    turma = _resolve_turma_for_legacy_form(class_id, class_name, course)
    return course, turma


def _resolve_existing_course(course_id, course_name):
    if course_id:
        try:
            parsed_id = int(course_id)
        except ValueError:
            raise StudentRegistrationError("Curso invalido.")

        course = Curso.query.get(parsed_id)
        if not course:
            raise StudentRegistrationError("Curso nao encontrado. Selecione um curso ja cadastrado.")
        return course

    if course_name:
        course = Curso.query.filter(Curso.nome.ilike(course_name)).first()
        if course:
            return course

    raise StudentRegistrationError("Selecione um curso ja cadastrado.")


def _resolve_existing_turma(class_id, class_name, course):
    if not course:
        raise StudentRegistrationError("Selecione um curso ja cadastrado antes da turma.")

    if class_id:
        try:
            parsed_id = int(class_id)
        except ValueError:
            raise StudentRegistrationError("Turma invalida.")

        turma = Turma.query.get(parsed_id)
        if not turma:
            raise StudentRegistrationError("Turma nao encontrada. Selecione uma turma ja cadastrada.")
        if turma.curso_id != course.id:
            raise StudentRegistrationError("A turma selecionada nao pertence ao curso escolhido.")
        return turma

    if class_name:
        turma = Turma.query.filter(
            Turma.curso_id == course.id,
            Turma.nome.ilike(class_name),
        ).first()
        if turma:
            return turma

    raise StudentRegistrationError("Selecione uma turma ja cadastrada para o curso escolhido.")


def _resolve_course_for_legacy_form(course_id, course_name):
    if course_id:
        return _resolve_existing_course(course_id, course_name)
    return _get_or_create_course(course_name)


def _resolve_turma_for_legacy_form(class_id, class_name, course):
    if class_id:
        return _resolve_existing_turma(class_id, class_name, course)
    return _get_or_create_turma(class_name, course)


def _get_or_create_course(course_name):
    course_name = _none_if_empty(course_name)
    if not course_name:
        raise StudentRegistrationError("Informe o curso.")

    course = Curso.query.filter(Curso.nome.ilike(course_name)).first()
    if course:
        return course

    course = Curso(nome=course_name)
    db.session.add(course)
    db.session.flush()
    return course


def _get_or_create_turma(class_name, course):
    class_name = _none_if_empty(class_name)
    if not class_name:
        raise StudentRegistrationError("Informe a turma.")
    if not course:
        raise StudentRegistrationError("Informe o curso antes da turma.")

    turma = Turma.query.filter(
        Turma.curso_id == course.id,
        Turma.nome.ilike(class_name),
    ).first()
    if turma:
        return turma

    turma = Turma(
        nome=class_name,
        curso_id=course.id,
        semestre="1",
        data_inicio=date.today(),
        data_fim=None,
    )
    db.session.add(turma)
    db.session.flush()
    return turma


def _split_full_name(full_name):
    parts = full_name.strip().split(" ", 1)
    return parts[0] if parts else "", parts[1] if len(parts) > 1 else ""


def _first_non_empty(data, *keys):
    for key in keys:
        value = _none_if_empty(data.get(key))
        if value is not None:
            return value
    return None


def _norm(value):
    return (value or "").strip()


def _none_if_empty(value):
    value = _norm(value)
    return value if value != "" else None
