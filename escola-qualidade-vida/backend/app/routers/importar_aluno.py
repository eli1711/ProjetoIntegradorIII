# app/routers/importar_alunos.py
import csv
import io
from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.aluno import Aluno, only_digits
from app.models.responsavel import Responsavel

import_bp = Blueprint("import_alunos", __name__, url_prefix="/alunos")

def str_to_bool(value):
    return str(value).strip().lower() in ["true", "1", "sim", "yes", "y", "t", "on"]

def parse_date_yyyy_mm_dd(s):
    if not s:
        return None
    s = s.strip()
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None

def calc_idade(dt):
    if not dt:
        return None
    hoje = date.today()
    return hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))

@import_bp.route("/importar_csv", methods=["POST"])
def importar_csv():
    if "arquivo" not in request.files:
        return jsonify({"erro": "Arquivo não enviado"}), 400

    f = request.files["arquivo"]
    if not f.filename.lower().endswith(".csv"):
        return jsonify({"erro": "Envie um arquivo .csv"}), 400

    try:
        content = f.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return jsonify({"erro": "CSV deve estar em UTF-8"}), 400

    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return jsonify({"erro": "CSV sem cabeçalhos"}), 400

    obrigatorios = {
        "matricula", "nome_completo", "cpf", "data_nascimento",
        "endereco", "cep", "bairro", "municipio",
        "curso", "tipo_curso", "turma",
    }

    headers = set(h.strip() for h in reader.fieldnames)
    faltam_headers = sorted(obrigatorios - headers)
    if faltam_headers:
        return jsonify({"erro": "Cabeçalhos obrigatórios ausentes", "faltando": faltam_headers}), 400

    relatorio = []
    sucesso = pulos = erros = 0

    for idx, row in enumerate(reader, start=2):
        try:
            row = { (k or "").strip(): (v or "").strip() for k, v in row.items() }

            missing = [k for k in obrigatorios if not row.get(k)]
            if missing:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - faltando {missing}")
                continue

            cpf = only_digits(row.get("cpf"))
            if not cpf or len(cpf) != 11:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - CPF inválido")
                continue

            if Aluno.query.filter_by(cpf=cpf).first():
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - CPF já cadastrado")
                continue

            data_nasc = parse_date_yyyy_mm_dd(row.get("data_nascimento"))
            if not data_nasc:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - data_nascimento inválida")
                continue

            idade = calc_idade(data_nasc)
            if idade is None:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - não foi possível calcular idade")
                continue

            cep = only_digits(row.get("cep"))
            if not cep or len(cep) != 8:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - CEP inválido")
                continue

            pne = str_to_bool(row.get("pne"))
            pne_desc = row.get("pne_descricao") or None

            empresa = row.get("empresa_aprendizagem") or None
            cnpj = only_digits(row.get("cnpj_empresa"))
            if cnpj and len(cnpj) != 14:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - CNPJ inválido")
                continue

            # Responsável se menor
            responsavel_obj = None
            if idade < 18:
                r_nome = (row.get("responsavel_nome_completo") or "").strip()
                r_parentesco = (row.get("responsavel_parentesco") or "").strip()
                r_tel = only_digits(row.get("responsavel_telefone") or "")

                if not r_nome or not r_parentesco or not r_tel:
                    pulos += 1
                    relatorio.append(f"Linha {idx}: pulada - menor de idade sem dados obrigatórios do responsável")
                    continue

                r_cep = only_digits(row.get("responsavel_cep"))
                if r_cep and len(r_cep) != 8:
                    pulos += 1
                    relatorio.append(f"Linha {idx}: pulada - CEP do responsável inválido")
                    continue

                responsavel_obj = Responsavel(
                    nome_completo=r_nome,
                    parentesco=r_parentesco,
                    telefone=r_tel,
                    endereco=(row.get("responsavel_endereco") or "").strip() or None,
                    cep=r_cep,
                    bairro=(row.get("responsavel_bairro") or "").strip() or None,
                    municipio=(row.get("responsavel_municipio") or "").strip() or None,
                )
                db.session.add(responsavel_obj)
                db.session.flush()

            aluno = Aluno(
                matricula=row["matricula"],
                nome_completo=row["nome_completo"],
                nome_social=row.get("nome_social") or None,

                cpf=cpf,
                data_nascimento=data_nasc,

                endereco=row["endereco"],
                cep=cep,
                bairro=row["bairro"],
                municipio=row["municipio"],

                telefone=only_digits(row.get("telefone") or "") or None,
                celular=only_digits(row.get("celular") or "") or None,

                curso=row["curso"],
                tipo_curso=row["tipo_curso"],
                turma=row["turma"],

                empresa_aprendizagem=empresa,
                cnpj_empresa=cnpj,

                pne=pne,
                pne_descricao=pne_desc if pne else None,

                parceria_novo_ensino_medio=row.get("parceria_novo_ensino_medio") or None,

                responsavel_id=(responsavel_obj.id if responsavel_obj else None),
            )
            aluno.normalize()

            db.session.add(aluno)
            sucesso += 1

        except Exception as e:
            erros += 1
            relatorio.append(f"Linha {idx}: erro - {e}")

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Falha no commit do CSV")
        return jsonify({"erro": "Erro ao salvar no banco"}), 500

    return jsonify({
        "mensagem": "Importação finalizada",
        "sucesso": sucesso,
        "pulos": pulos,
        "erros": erros,
        "relatorio": relatorio,
    }), 200
