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
        try:
            return datetime.strptime(s, "%d/%m/%Y").date()
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

    # ✅ CAMPOS OBRIGATÓRIOS AJUSTADOS PARA O SEU BANCO
    # Seu banco tem: cidade, bairro, rua (não endereco, municipio)
    obrigatorios = {
        "matricula", "nome_completo", "cpf", "data_nascimento",
        "cidade", "bairro", "rua",  # Ajustados para seu banco
        "curso", "turma"  # tipo_curso não existe no seu banco
    }

    headers = set(h.strip().lower() for h in reader.fieldnames)
    # Mapear nomes possíveis dos campos
    header_map = {}
    for h in reader.fieldnames:
        header_map[h.strip().lower()] = h
    
    # Verificar se temos os campos obrigatórios
    faltam_headers = []
    for campo in obrigatorios:
        if campo not in header_map:
            # Verificar variações possíveis
            if campo == "nome_completo" and "nome" in header_map:
                continue
            elif campo == "data_nascimento" and ("data nascimento" in header_map or "nascimento" in header_map):
                continue
            elif campo == "cidade" and ("municipio" in header_map or "município" in header_map):
                continue
            elif campo == "rua" and ("endereco" in header_map or "endereço" in header_map or "logradouro" in header_map):
                continue
            faltam_headers.append(campo)
    
    if faltam_headers:
        return jsonify({"erro": "Cabeçalhos obrigatórios ausentes", "faltando": sorted(faltam_headers)}), 400

    relatorio = []
    sucesso = pulos = erros = 0

    for idx, row in enumerate(reader, start=2):
        try:
            row = { (k or "").strip(): (v or "").strip() for k, v in row.items() }
            
            # Mapear campos com nomes diferentes
            def get_field(field_name, default=None):
                # Tenta o nome exato primeiro
                if field_name in row:
                    return row[field_name]
                # Tenta lowercase
                field_lower = field_name.lower()
                for key in row.keys():
                    if key.lower() == field_lower:
                        return row[key]
                # Tenta variações comuns
                variations = {
                    "nome_completo": ["nome", "nome completo"],
                    "data_nascimento": ["data nascimento", "nascimento", "datanascimento"],
                    "cidade": ["municipio", "município", "localidade"],
                    "rua": ["endereco", "endereço", "logradouro", "endereço completo"],
                    "bairro": ["bairro", "zona", "distrito"],
                    "curso": ["curso", "nome curso", "curso_nome"],
                    "turma": ["turma", "classe", "sala"],
                    "empresa_contratante": ["empresa", "empresa aprendizagem", "empresa_aprendizagem", "empresacontrato"],
                    "cnpj_empresa": ["cnpj", "cnpj empresa"],
                    "outras_informacoes": ["parceria novo ensino medio", "parceria_novo_ensino_medio", "observacoes", "observações"]
                }
                
                if field_name in variations:
                    for var in variations[field_name]:
                        if var in row:
                            return row[var]
                
                return default

            # Coletar dados obrigatórios
            matricula = get_field("matricula")
            nome_completo = get_field("nome_completo")
            cpf_raw = get_field("cpf")
            data_nasc_raw = get_field("data_nascimento")
            cidade = get_field("cidade")
            bairro = get_field("bairro")
            rua = get_field("rua")
            curso = get_field("curso")
            turma = get_field("turma")

            # Verificar campos obrigatórios
            campos_obrigatorios = [
                ("matricula", matricula),
                ("nome_completo", nome_completo),
                ("cpf", cpf_raw),
                ("data_nascimento", data_nasc_raw),
                ("cidade", cidade),
                ("bairro", bairro),
                ("rua", rua),
                ("curso", curso),
                ("turma", turma)
            ]
            
            missing = [nome for nome, valor in campos_obrigatorios if not valor]
            if missing:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - faltando {', '.join(missing)}")
                continue

            # Processar CPF
            cpf = only_digits(cpf_raw)
            if not cpf or len(cpf) != 11:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - CPF inválido: {cpf_raw}")
                continue

            if Aluno.query.filter_by(cpf=cpf).first():
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - CPF já cadastrado: {cpf}")
                continue

            # Verificar matrícula única
            if Aluno.query.filter_by(matricula=matricula).first():
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - Matrícula já cadastrada: {matricula}")
                continue

            # Processar data de nascimento
            data_nasc = parse_date_yyyy_mm_dd(data_nasc_raw)
            if not data_nasc:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - data_nascimento inválida: {data_nasc_raw}")
                continue

            idade = calc_idade(data_nasc)
            if idade is None:
                pulos += 1
                relatorio.append(f"Linha {idx}: pulada - não foi possível calcular idade")
                continue

            # Separar nome completo em nome e sobrenome
            nome = ""
            sobrenome = ""
            if nome_completo:
                partes = nome_completo.strip().split(' ', 1)
                nome = partes[0] if partes else ""
                sobrenome = partes[1] if len(partes) > 1 else ""

            # Processar outros campos
            telefone = only_digits(get_field("telefone", "")) or None
            empregado = get_field("empregado", "nao").lower()
            if empregado not in ["sim", "nao"]:
                empregado = "nao"
            
            mora_com_quem = get_field("mora_com_quem") or None
            sobre_aluno = get_field("sobre_aluno") or None
            
            data_inicio_curso = parse_date_yyyy_mm_dd(get_field("data_inicio_curso"))
            empresa_contratante = get_field("empresa_contratante") or None
            
            # Processar PNE (pessoa_com_deficiencia)
            pne_raw = get_field("pessoa_com_deficiencia") or get_field("pne", "")
            pessoa_com_deficiencia = str_to_bool(pne_raw)
            
            outras_informacoes = get_field("outras_informacoes") or None
            
            # Processar linha_atendimento
            linha_atendimento = get_field("linha_atendimento", "CAI").upper()
            if linha_atendimento not in ["CAI", "CT", "CST"]:
                linha_atendimento = "CAI"
            
            # Processar escola_integrada
            escola_integrada = get_field("escola_integrada", "Nenhuma")
            if escola_integrada not in ["SESI", "SEDUC", "Nenhuma"]:
                escola_integrada = "Nenhuma"

            # Processar Responsável se menor de idade
            responsavel_obj = None
            if idade < 18:
                r_nome = get_field("responsavel_nome_completo", "").strip()
                r_parentesco = get_field("responsavel_parentesco", "").strip()
                r_tel = only_digits(get_field("responsavel_telefone", ""))

                if not r_nome or not r_parentesco or not r_tel:
                    pulos += 1
                    relatorio.append(f"Linha {idx}: pulada - menor de idade sem dados obrigatórios do responsável")
                    continue

                responsavel_obj = Responsavel(
                    nome=r_nome,
                    sobrenome="",  # Você pode ajustar conforme seu model
                    parentesco=r_parentesco,
                    telefone=r_tel or None,
                    cidade=get_field("responsavel_cidade") or get_field("responsavel_municipio", "").strip() or None,
                    bairro=get_field("responsavel_bairro", "").strip() or None,
                    rua=get_field("responsavel_endereco", "").strip() or None,
                )
                db.session.add(responsavel_obj)
                db.session.flush()

            # Criar objeto Aluno com a ESTRUTURA CORRETA DO SEU BANCO
            aluno = Aluno(
                # CPF OBRIGATÓRIO
                cpf=cpf,
                
                # Nome completo e dividido
                nome_completo=nome_completo,
                nome=nome,
                sobrenome=sobrenome,
                
                # Dados obrigatórios
                matricula=matricula,
                cidade=cidade,
                bairro=bairro,
                rua=rua,
                idade=idade,
                empregado=empregado,
                
                # Dados acadêmicos
                curso=curso,
                turma=turma,
                
                # Dados pessoais
                telefone=telefone,
                data_nascimento=data_nasc,
                linha_atendimento=linha_atendimento,
                escola_integrada=escola_integrada,
                
                # Campos opcionais
                mora_com_quem=mora_com_quem,
                sobre_aluno=sobre_aluno,
                data_inicio_curso=data_inicio_curso,
                empresa_contratante=empresa_contratante,
                pessoa_com_deficiencia=pessoa_com_deficiencia,
                outras_informacoes=outras_informacoes,
                
                # Relacionamentos
                responsavel_id=(responsavel_obj.id if responsavel_obj else None),
            )
            
            # Normaliza dados (CPF, telefone, etc.)
            aluno.normalize()
            
            db.session.add(aluno)
            sucesso += 1
            relatorio.append(f"Linha {idx}: OK - {nome_completo} (CPF: {cpf}, Matrícula: {matricula})")

        except Exception as e:
            erros += 1
            relatorio.append(f"Linha {idx}: ERRO - {str(e)}")
            current_app.logger.error(f"Erro na linha {idx}: {str(e)}", exc_info=True)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Falha no commit do CSV")
        relatorio.append(f"ERRO NO COMMIT: {str(e)}")
        return jsonify({
            "erro": "Erro ao salvar no banco",
            "sucesso": sucesso,
            "pulos": pulos,
            "erros": erros,
            "relatorio": relatorio
        }), 500

    return jsonify({
        "mensagem": "Importação finalizada",
        "sucesso": sucesso,
        "pulos": pulos,
        "erros": erros,
        "relatorio": relatorio,
    }), 200


@import_bp.route("/csv_modelo", methods=["GET"])
def csv_modelo():
    """
    Retorna um modelo CSV com os campos necessários
    AJUSTADO PARA SUA ESTRUTURA DE BANCO
    """
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalhos ajustados para sua estrutura
    headers = [
        # Obrigatórios
        "matricula",
        "nome_completo", 
        "cpf",
        "data_nascimento",
        "cidade",        # Seu banco tem cidade (não municipio)
        "bairro",
        "rua",           # Seu banco tem rua (não endereco)
        "curso",
        "turma",
        
        # Campos do sistema que são obrigatórios no banco
        "idade",          # Pode calcular ou informar
        "empregado",      # sim ou nao
        "linha_atendimento",  # CAI, CT ou CST
        "escola_integrada",   # SESI, SEDUC ou Nenhuma
        
        # Opcionais
        "telefone",
        "mora_com_quem",
        "sobre_aluno",
        "data_inicio_curso",
        "empresa_contratante",
        "pessoa_com_deficiencia",  # true/false
        "outras_informacoes",
        
        # Responsável (obrigatório se menor)
        "responsavel_nome_completo",
        "responsavel_parentesco",
        "responsavel_telefone",
        "responsavel_cidade",
        "responsavel_bairro",
        "responsavel_endereco"
    ]
    
    writer.writerow(headers)
    
    # Exemplo de linha ADULTO
    writer.writerow([
        "MAT2024001",  # matricula
        "João da Silva",  # nome_completo
        "123.456.789-00",  # cpf
        "2000-06-15",  # data_nascimento (maior de idade)
        "Belo Horizonte",  # cidade
        "Centro",  # bairro
        "Rua das Flores, 123",  # rua
        "Informática Básica",  # curso
        "Turma A",  # turma
        "24",  # idade
        "sim",  # empregado
        "CAI",  # linha_atendimento
        "Nenhuma",  # escola_integrada
        "(31) 9999-8888",  # telefone
        "",  # mora_com_quem
        "Aluno dedicado",  # sobre_aluno
        "2024-02-01",  # data_inicio_curso
        "Empresa ABC Ltda",  # empresa_contratante
        "false",  # pessoa_com_deficiencia
        "Parceria com Escola Estadual",  # outras_informacoes
        "", "", "", "", "", ""  # responsável vazio (maior de idade)
    ])
    
    # Exemplo de linha MENOR
    writer.writerow([
        "MAT2024002",  # matricula
        "Maria Oliveira",  # nome_completo
        "987.654.321-00",  # cpf
        "2010-03-20",  # data_nascimento (menor)
        "Belo Horizonte",  # cidade
        "Savassi",  # bairro
        "Av. Brasil, 456",  # rua
        "Administração",  # curso
        "Turma B",  # turma
        "14",  # idade
        "nao",  # empregado
        "CT",  # linha_atendimento
        "SESI",  # escola_integrada
        "(31) 3333-4444",  # telefone
        "Pais",  # mora_com_quem
        "Boa aluna",  # sobre_aluno
        "2024-03-01",  # data_inicio_curso
        "",  # empresa_contratante
        "true",  # pessoa_com_deficiencia
        "Necessita adaptação",  # outras_informacoes
        "Carlos Oliveira",  # responsavel_nome_completo
        "Pai",  # responsavel_parentesco
        "(31) 8888-7777",  # responsavel_telefone
        "Belo Horizonte",  # responsavel_cidade
        "Savassi",  # responsavel_bairro
        "Av. Brasil, 456"  # responsavel_endereco
    ])
    
    output.seek(0)
    
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename="modelo_alunos.csv"'
    }