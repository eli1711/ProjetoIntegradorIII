# app/routers/aluno.py
import os
import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.aluno import Aluno, only_digits
from app.models.responsavel import Responsavel
from app.models.empresa import Empresa
from app.models.turma import Turma
from app.models.curso import Curso

aluno_bp = Blueprint("aluno", __name__, url_prefix="/alunos")

# -------------------------
# Utilitários
# -------------------------
def str_to_bool(value):
    return str(value).lower() in ["true", "1", "on", "t", "yes", "y", "sim"]

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None
    except ValueError:
        return None

def _norm(v: str) -> str:
    return (v or "").strip()

def _none_if_empty(v):
    v = _norm(v)
    return v if v != "" else None

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def _save_photo(file_storage, desired_name_base: str) -> str:
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise ValueError("Extensão de imagem inválida. Use JPG, PNG, GIF ou WEBP.")

    base = secure_filename((desired_name_base or "aluno").lower())
    filename = f"{base}{ext}"
    dest = os.path.join(upload_dir, filename)

    i = 1
    while os.path.exists(dest):
        filename = f"{base}_{i}{ext}"
        dest = os.path.join(upload_dir, filename)
        i += 1

    file_storage.save(dest)
    current_app.logger.info(f"🖼️ Foto salva em: {dest}")
    return filename

def _json_aluno(a: Aluno):
    turma = a.turma_relacionada
    curso = a.curso_relacionado
    return {
        "id": a.id,
        "cpf": a.cpf,  # ✅ ADICIONADO CPF
        "nome": f"{a.nome} {a.sobrenome}",
        "nome_completo": a.nome_completo,  # ✅ ADICIONADO nome_completo
        "matricula": a.matricula,
        "foto": a.foto,
        "foto_url": f"/uploads/{a.foto}" if a.foto else None,
        "curso": (curso.nome if curso else (a.curso or None)),
        "curso_id": a.curso_id,
        "turma": (turma.nome if turma else (a.turma or None)),
        "turma_id": a.turma_id,
        "turma_nome": turma.nome if turma else None,
        "turma_semestre": turma.semestre if turma else None,
        "cidade": a.cidade, "bairro": a.bairro, "rua": a.rua,
        "telefone": a.telefone,
        "data_nascimento": a.data_nascimento.isoformat() if a.data_nascimento else None,
        "linha_atendimento": a.linha_atendimento,
        "escola_integrada": a.escola_integrada,
        "empresa_contratante": a.empresa_contratante,
        "data_inicio_curso": a.data_inicio_curso.isoformat() if a.data_inicio_curso else None,
        "mora_com_quem": a.mora_com_quem,
        "sobre_aluno": a.sobre_aluno,
        "pessoa_com_deficiencia": bool(a.pessoa_com_deficiencia),
        "outras_informacoes": a.outras_informacoes,
    }

# Domínios válidos
_LINHAS_AT = {"CAI", "CT", "CST"}
_ESCOLAS = {"SESI", "SEDUC", "Nenhuma"}
_EMPREGADO = {"sim", "nao"}

# -------------------------
# CADASTRAR ALUNO COM CPF OBRIGATÓRIO (ROTA ALTERNATIVA)
# -------------------------
@aluno_bp.route("/cadastrar", methods=["POST"])
def cadastrar_aluno_com_cpf():
    """
    Cadastra um novo aluno via formulário web com CPF OBRIGATÓRIO
    (Esta é uma rota alternativa à /cadastro/alunos)
    """
    try:
        data = request.form
        current_app.logger.info(f"Dados recebidos para cadastro: {dict(data)}")
        
        # 1. VALIDAÇÃO CPF OBRIGATÓRIO
        cpf = data.get('cpf')
        if not cpf:
            return jsonify({"erro": "CPF é obrigatório"}), 400
        
        # Remove formatação do CPF
        cpf_limpo = only_digits(cpf)
        
        # Validação básica
        if not cpf_limpo or len(cpf_limpo) != 11:
            return jsonify({"erro": "CPF deve conter 11 dígitos"}), 400
        
        # Verificar se CPF já existe
        aluno_existente = Aluno.query.filter_by(cpf=cpf_limpo).first()
        if aluno_existente:
            return jsonify({"erro": "CPF já cadastrado"}), 400
        
        # 2. Verificar matrícula única
        matricula = data.get('matricula')
        if matricula and Aluno.query.filter_by(matricula=matricula).first():
            return jsonify({"erro": "Matrícula já cadastrada"}), 400
        
        # 3. Processar nome_completo se existir
        nome_completo = data.get('nome_completo', '')
        nome = data.get('nome', '')
        sobrenome = data.get('sobrenome', '')
        
        if nome_completo and not nome:
            # Dividir nome_completo em nome e sobrenome
            partes = nome_completo.strip().split(' ', 1)
            nome = partes[0] if partes else ''
            sobrenome = partes[1] if len(partes) > 1 else ''
        elif nome and sobrenome and not nome_completo:
            # Constrói nome_completo se não fornecido
            nome_completo = f"{nome} {sobrenome}"
        
        # 4. Criar aluno COM CPF OBRIGATÓRIO
        aluno = Aluno(
            nome=nome,
            sobrenome=sobrenome,
            nome_completo=nome_completo,
            cpf=cpf_limpo,  # CPF OBRIGATÓRIO
            matricula=matricula,
            cidade=data.get('cidade', ''),
            bairro=data.get('bairro', ''),
            rua=data.get('rua', ''),
            telefone=only_digits(data.get('telefone')),
            # Campos com valores padrão
            linha_atendimento=data.get('linha_atendimento', 'CAI'),
            escola_integrada=data.get('escola_integrada', 'Nenhuma'),
            empregado=data.get('empregado', 'nao'),
            pessoa_com_deficiencia=str_to_bool(data.get('pessoa_com_deficiencia', False))
        )
        
        # Campo idade
        idade = data.get('idade')
        if idade:
            try:
                aluno.idade = int(idade)
            except:
                # Calcular a partir da data de nascimento
                data_nascimento = data.get('data_nascimento')
                if data_nascimento:
                    try:
                        aluno.data_nascimento = parse_date(data_nascimento)
                        if aluno.data_nascimento:
                            hoje = date.today()
                            aluno.idade = hoje.year - aluno.data_nascimento.year - (
                                (hoje.month, hoje.day) < (aluno.data_nascimento.month, aluno.data_nascimento.day)
                            )
                        else:
                            aluno.idade = 18
                    except:
                        aluno.idade = 18
                else:
                    aluno.idade = 18
        
        # Data de nascimento
        if data.get('data_nascimento'):
            aluno.data_nascimento = parse_date(data.get('data_nascimento'))
        
        # Campos opcionais
        if data.get('mora_com_quem'):
            aluno.mora_com_quem = data.get('mora_com_quem')
        if data.get('sobre_aluno'):
            aluno.sobre_aluno = data.get('sobre_aluno')
        if data.get('data_inicio_curso'):
            aluno.data_inicio_curso = parse_date(data.get('data_inicio_curso'))
        if data.get('empresa_contratante'):
            aluno.empresa_contratante = data.get('empresa_contratante')
        if data.get('outras_informacoes'):
            aluno.outras_informacoes = data.get('outras_informacoes')
        if data.get('curso'):
            aluno.curso = data.get('curso')
        if data.get('turma'):
            aluno.turma = data.get('turma')
        
        # Processar foto
        if 'foto' in request.files and request.files['foto'].filename:
            foto = request.files['foto']
            filename = _save_photo(foto, nome_completo or nome)
            aluno.foto = filename
        
        # Normaliza dados (incluindo CPF já limpo)
        aluno.normalize()
        
        db.session.add(aluno)
        db.session.commit()
        
        return jsonify({
            "mensagem": "Aluno cadastrado com sucesso!",
            "aluno_id": aluno.id,
            "cpf": aluno.cpf,
            "matricula": aluno.matricula
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao cadastrar aluno: {str(e)}", exc_info=True)
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500


# -------------------------
# CONSULTAR ALUNO POR CPF
# -------------------------
@aluno_bp.route("/por-cpf/<string:cpf>", methods=["GET"])
def consultar_aluno_por_cpf(cpf):
    """
    Consulta um aluno pelo CPF
    """
    try:
        # Limpar CPF
        cpf_limpo = only_digits(cpf)
        
        if not cpf_limpo or len(cpf_limpo) != 11:
            return jsonify({"erro": "CPF inválido"}), 400
        
        aluno = Aluno.query.filter_by(cpf=cpf_limpo).first()
        
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        
        return jsonify(_json_aluno(aluno)), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao consultar aluno por CPF: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500


# -------------------------
# Saúde do blueprint
# -------------------------
@aluno_bp.route("/", methods=["GET"])
def listar_alunos():
    return jsonify({"mensagem": "Blueprint 'aluno_bp' ativo e funcionando corretamente!"}), 200

# -------------------------
# MODELO CSV (por NOME de curso/turma; IDs também aceitos)
# -------------------------
@aluno_bp.route("/csv_modelo", methods=["GET"])
def csv_modelo_alunos():
    """
    CSV de exemplo:
      - Usa 'curso_nome' e 'turma_nome' (opcionais). IDs também são aceitos como alternativa.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        # obrigatórios
        "nome","sobrenome","matricula","cidade","bairro","rua","idade",
        "linha_atendimento","escola_integrada",
        # nomes (preferenciais) - opcionais
        "curso_nome","turma_nome",
        # ids (alternativa) - opcionais
        "curso_id","turma_id",
        # outros opcionais
        "telefone","data_nascimento","empregado","mora_com_quem","sobre_aluno",
        "data_inicio_curso","empresa_contratante","pessoa_com_deficiencia","outras_informacoes",
        "cpf"  # ✅ ADICIONADO CPF NO MODELO CSV
    ]
    writer.writerow(headers)
    writer.writerow([
        "Ana","Silva","MAT001","Belo Horizonte","Centro","Rua A","16",
        "CAI","SESI",
        "Informática Básica","Turma 101",
        "","","(31) 99999-9999","2009-05-10","nao","","",
        "2025-02-01","","false","","12345678901"
    ])
    writer.writerow([
        "Bruno","Souza","MAT002","BH","Savassi","Rua B","19",
        "CT","Nenhuma",
        "", "",  # curso_nome, turma_nome
        "2","12",  # usando IDs como alternativa
        "","2006-11-20","sim","Pais","Aluno destaque",
        "2025-03-01","Empresa X","true","Necessita adaptação de prova","98765432109"
    ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name="modelo_alunos.csv",
    )

# -------------------------
# IMPORTAR CSV (aceita NOME ou ID; salva nomes; resolve FKs quando possível)
# -------------------------
@aluno_bp.route("/importar_csv", methods=["POST"])
def importar_csv_alunos():
    """
    Importa um CSV e cria registros na tabela 'aluno'.
    Agora com CPF obrigatório!
    """
    if "arquivo" not in request.files or not request.files["arquivo"].filename:
        return jsonify({"erro": "Envie um arquivo CSV no campo 'arquivo'."}), 400

    f = request.files["arquivo"]
    try:
        content = f.read()
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        obrig = {
            "nome","sobrenome","matricula","cidade","bairro","rua","idade",
            "linha_atendimento","escola_integrada","cpf"  # ✅ CPF OBRIGATÓRIO AGORA
        }

        if not reader.fieldnames:
            return jsonify({"erro": "CSV sem cabeçalho."}), 400

        field_map = {(h or "").strip(): h for h in reader.fieldnames}
        missing_cols = obrig - set(field_map.keys())
        if missing_cols:
            return jsonify({"erro": f"CSV faltando colunas obrigatórias: {', '.join(sorted(missing_cols))}"}), 400

        sucesso = pulos = erros = 0
        rel = []

        for i, row in enumerate(reader, start=2):
            try:
                def col(key):
                    return row.get(field_map.get(key, key))

                # -------- obrigatórios
                nome = _none_if_empty(col("nome"))
                sobrenome = _none_if_empty(col("sobrenome"))
                matricula = _none_if_empty(col("matricula"))
                cidade = _none_if_empty(col("cidade"))
                bairro = _none_if_empty(col("bairro"))
                rua = _none_if_empty(col("rua"))
                idade_raw = _none_if_empty(col("idade"))
                linha_atendimento = _none_if_empty(col("linha_atendimento"))
                escola_integrada = _none_if_empty(col("escola_integrada"))
                cpf_raw = _none_if_empty(col("cpf"))

                if not all([nome, sobrenome, matricula, cidade, bairro, rua, idade_raw,
                            linha_atendimento, escola_integrada, cpf_raw]):
                    raise ValueError("Campos obrigatórios vazios.")

                # Valida CPF
                cpf = only_digits(cpf_raw)
                if not cpf or len(cpf) != 11:
                    raise ValueError("CPF inválido (deve conter 11 dígitos).")
                
                # Verifica se CPF já existe
                if Aluno.query.filter_by(cpf=cpf).first():
                    pulos += 1
                    rel.append(f"[Linha {i}] CPF '{cpf_raw}' já cadastrado — pulado.")
                    continue

                try:
                    idade = int(idade_raw)
                except Exception:
                    raise ValueError("idade inválida (inteiro).")

                la = linha_atendimento.upper()
                if la not in _LINHAS_AT:
                    raise ValueError("linha_atendimento deve ser CAI, CT ou CST.")
                if escola_integrada not in _ESCOLAS:
                    raise ValueError("escola_integrada deve ser SESI, SEDUC ou Nenhuma.")

                # duplicidade de matrícula
                if Aluno.query.filter_by(matricula=matricula).first():
                    pulos += 1
                    rel.append(f"[Linha {i}] Matrícula '{matricula}' já existe — pulado.")
                    continue

                # -------- opcionais simples
                telefone = _none_if_empty(col("telefone"))
                empregado = (_norm(col("empregado")) or "nao").lower()
                if empregado not in _EMPREGADO:
                    raise ValueError("empregado deve ser 'sim' ou 'nao'.")

                mora_com_quem = _none_if_empty(col("mora_com_quem"))
                sobre_aluno = _none_if_empty(col("sobre_aluno"))
                data_nascimento = parse_date(_none_if_empty(col("data_nascimento")))
                data_inicio_curso = parse_date(_none_if_empty(col("data_inicio_curso")))
                empresa_contratante = _none_if_empty(col("empresa_contratante"))
                pcd = str_to_bool(_norm(col("pessoa_com_deficiencia")))
                outras_informacoes = _none_if_empty(col("outras_informacoes"))

                # -------- curso/turma por NOME ou ID (suave)
                curso_nome = _none_if_empty(col("curso_nome"))
                turma_nome = _none_if_empty(col("turma_nome"))
                curso_id_raw = _none_if_empty(col("curso_id"))
                turma_id_raw = _none_if_empty(col("turma_id"))

                resolved_curso = None
                resolved_turma = None

                # Tenta por ID, mas NÃO erra se não achar
                if curso_id_raw:
                    try:
                        resolved_curso = Curso.query.get(int(curso_id_raw))
                        if not resolved_curso:
                            rel.append(f"[Linha {i}] Aviso: curso_id '{curso_id_raw}' não encontrado — ignorado.")
                    except Exception:
                        rel.append(f"[Linha {i}] Aviso: curso_id inválido — ignorado.")

                if turma_id_raw:
                    try:
                        resolved_turma = Turma.query.get(int(turma_id_raw))
                        if not resolved_turma:
                            rel.append(f"[Linha {i}] Aviso: turma_id '{turma_id_raw}' não encontrado — ignorado.")
                    except Exception:
                        rel.append(f"[Linha {i}] Aviso: turma_id inválido — ignorado.")

                # Coerência entre IDs se ambos existem; se incoerente, ignora a turma
                if resolved_curso and resolved_turma and resolved_turma.curso_id != resolved_curso.id:
                    rel.append(f"[Linha {i}] Aviso: turma_id não pertence ao curso_id — turma ignorada.")
                    resolved_turma = None

                # Tenta resolver por NOME quando ainda não resolvido
                if not resolved_curso and curso_nome:
                    resolved_curso = Curso.query.filter(Curso.nome.ilike(curco_nome)).first()
                    if not resolved_curso:
                        rel.append(f"[Linha {i}] Aviso: curso_nome '{curso_nome}' não encontrado — gravado apenas como texto.")

                if not resolved_turma and turma_nome:
                    q_turma = Turma.query
                    if resolved_curso:
                        q_turma = q_turma.filter(Turma.curso_id == resolved_curso.id)
                    resolved_turma = q_turma.filter(Turma.nome.ilike(turma_nome)).first()
                    if not resolved_turma:
                        rel.append(f"[Linha {i}] Aviso: turma_nome '{turma_nome}' não encontrada — gravada apenas como texto.")
                    # se achou turma e não havia curso, infere
                    if resolved_turma and not resolved_curso:
                        resolved_curso = resolved_turma.curso_relacionado

                # Coerência final (se nome resolveu turma mas curso não bate)
                if resolved_turma and resolved_curso and resolved_turma.curso_id != resolved_curso.id:
                    rel.append(f"[Linha {i}] Aviso: turma localizada não pertence ao curso localizado — turma ignorada.")
                    resolved_turma = None

                curso_id_val = resolved_curso.id if resolved_curso else None
                turma_id_val = resolved_turma.id if resolved_turma else None
                curso_texto = (resolved_curso.nome if resolved_curso else curso_nome)
                turma_texto = (resolved_turma.nome if resolved_turma else turma_nome)

                # Constrói nome_completo
                nome_completo = f"{nome} {sobrenome}".strip()

                aluno = Aluno(
                    nome=nome,
                    sobrenome=sobrenome,
                    nome_completo=nome_completo,
                    cpf=cpf,  # ✅ CPF OBRIGATÓRIO
                    matricula=matricula,
                    cidade=cidade,
                    bairro=bairro,
                    rua=rua,
                    idade=idade,
                    empregado=empregado,
                    mora_com_quem=mora_com_quem,
                    sobre_aluno=sobre_aluno,
                    foto=None,
                    telefone=only_digits(telefone),
                    data_nascimento=data_nascimento,
                    linha_atendimento=la,
                    curso=curso_texto,     # salva nomes quando houver
                    turma=turma_texto,     # salva nomes quando houver
                    data_inicio_curso=data_inicio_curso,
                    empresa_contratante=empresa_contratante,
                    escola_integrada=escola_integrada,
                    pessoa_com_deficiencia=pcd,
                    outras_informacoes=outras_informacoes,
                    curso_id=curso_id_val, # FKs somente se resolvidos
                    turma_id=turma_id_val
                )

                db.session.add(aluno)
                db.session.commit()

                sucesso += 1
                rel.append(f"[Linha {i}] OK: {nome} {sobrenome} (CPF: {cpf}).")

            except Exception as ex:
                db.session.rollback()
                erros += 1
                rel.append(f"[Linha {i}] ERRO: {str(ex)}")

        return jsonify({
            "sucesso": sucesso,
            "pulos": pulos,
            "erros": erros,
            "relatorio": rel
        }), 200

    except UnicodeDecodeError:
        return jsonify({"erro": "Não foi possível ler o arquivo. Use CSV UTF-8."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Falha ao processar CSV.", "detalhes": str(e)}), 500

# -------------------------
# EDITAR ALUNO (dados)
# -------------------------
@aluno_bp.route("/<int:aluno_id>", methods=["PATCH"])
def editar_aluno(aluno_id: int):
    aluno = Aluno.query.get_or_404(aluno_id)
    data = request.get_json(silent=True) or {}

    # Atualiza apenas campos enviados; strings vazias viram None
    for field in ("cidade", "bairro", "rua", "telefone", "empresa_contratante",
                  "mora_com_quem", "sobre_aluno", "outras_informacoes", "curso", "turma"):
        if field in data:
            setattr(aluno, field, _none_if_empty(data[field]))

    if "pessoa_com_deficiencia" in data:
        aluno.pessoa_com_deficiencia = bool(data["pessoa_com_deficiencia"])

    if "data_nascimento" in data:
        aluno.data_nascimento = parse_date(_none_if_empty(data["data_nascimento"]))
    if "data_inicio_curso" in data:
        aluno.data_inicio_curso = parse_date(_none_if_empty(data["data_inicio_curso"]))

    if "linha_atendimento" in data and data["linha_atendimento"]:
        la = data["linha_atendimento"]
        if la not in _LINHAS_AT:
            return jsonify({"erro": "linha_atendimento inválida."}), 400
        aluno.linha_atendimento = la

    if "escola_integrada" in data and data["escola_integrada"]:
        ei = data["escola_integrada"]
        if ei not in _ESCOLAS:
            return jsonify({"erro": "escola_integrada inválida."}), 400
        aluno.escola_integrada = ei

    # Se vierem curso_nome/turma_nome na edição, também tento resolver os FKs (opcional)
    curso_nome = _none_if_empty(data.get("curso_nome"))
    turma_nome = _none_if_empty(data.get("turma_nome"))
    curso_id = data.get("curso_id", None)
    turma_id = data.get("turma_id", None)

    resolved_curso = None
    resolved_turma = None

    if turma_id not in (None, ""):
        t = Turma.query.get(int(turma_id))
        if not t:
            return jsonify({"erro": "turma_id não encontrado."}), 400
        resolved_turma = t
    if curso_id not in (None, ""):
        c = Curso.query.get(int(curso_id))
        if not c:
            return jsonify({"erro": "curso_id não encontrado."}), 400
        resolved_curso = c

    if not resolved_curso and curso_nome:
        resolved_curso = Curso.query.filter(Curso.nome.ilike(curso_nome)).first()
    if not resolved_turma and turma_nome:
        q_turma = Turma.query
        if resolved_curso:
            q_turma = q_turma.filter(Turma.curso_id == resolved_curso.id)
        resolved_turma = q_turma.filter(Turma.nome.ilike(turma_nome)).first()

    if resolved_turma and resolved_curso and resolved_turma.curso_id != resolved_curso.id:
        return jsonify({"erro": "A turma localizada não pertence ao curso localizado."}), 400

    if resolved_curso:
        aluno.curso_id = resolved_curso.id
        aluno.curso = resolved_curso.nome
    elif "curso_id" in data or "curso_nome" in data:
        # Se a edição explicitamente limpou
        if data.get("curso_id") in (None, "") and not curso_nome:
            aluno.curso_id = None

    if resolved_turma:
        aluno.turma_id = resolved_turma.id
        aluno.turma = resolved_turma.nome
    elif "turma_id" in data or "turma_nome" in data:
        if data.get("turma_id") in (None, "") and not turma_nome:
            aluno.turma_id = None

    # Normaliza dados após edição
    aluno.normalize()
    
    db.session.commit()
    return jsonify(_json_aluno(aluno)), 200

# -------------------------
# TROCAR FOTO DO ALUNO
# -------------------------
@aluno_bp.route("/<int:aluno_id>/foto", methods=["PUT"])
def trocar_foto(aluno_id: int):
    aluno = Aluno.query.get_or_404(aluno_id)

    if "foto" not in request.files or not request.files["foto"].filename:
        return jsonify({"erro": "Envie a imagem no campo 'foto'."}), 400

    file = request.files["foto"]
    try:
        novo_filename = _save_photo(file, aluno.nome)
        # remove antiga (se existir)
        if aluno.foto:
            try:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], aluno.foto)
                if os.path.exists(old_path):
                    os.remove(old_path)
                    current_app.logger.info(f"🗑️ Foto antiga removida: {old_path}")
            except Exception:
                pass

        aluno.foto = novo_filename
        db.session.commit()

        return jsonify({
            "mensagem": "Foto atualizada com sucesso!",
            "aluno_id": aluno.id,
            "foto": aluno.foto,
            "foto_url": f"/uploads/{aluno.foto}"
        }), 200

    except ValueError as ve:
        return jsonify({"erro": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro ao trocar foto do aluno")
        return jsonify({"erro": "Falha ao atualizar foto.", "detalhes": str(e)}), 500