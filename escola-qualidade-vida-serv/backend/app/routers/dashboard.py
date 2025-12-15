from flask import Blueprint, request, jsonify, Response
from sqlalchemy import func, or_
from app.extensions import db
from app.models.aluno import Aluno, only_digits  # ✅ pega o only_digits do seu model
from app.models.ocorrencia import Ocorrencia
from app.models.turma import Turma
from app.models.curso import Curso
import io, csv

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


# ==========================
# HELPERS (FILTROS)
# ==========================
def _get_str(name: str) -> str:
    v = request.args.get(name, '')
    return (v or '').strip()

def _get_int(name: str, default: int = 0) -> int:
    try:
        return int(request.args.get(name, default))
    except:
        return default


def aplicar_filtros_alunos(query):
    """
    Aplica filtros do dashboard sobre a query de Aluno.
    Filtros:
      - statusTurma: 'todas' | 'ativas' | 'finalizadas'
      - cursoId: id do curso
      - buscaAluno: Nome OU CPF (com/sem máscara) OU matrícula (se existir)
      - buscaTurma: Nome da turma (via Turma.nome OU Aluno.turma)
    """
    status_turma = _get_str('statusTurma') or 'todas'
    curso_id = _get_str('cursoId')
    busca_aluno = _get_str('buscaAluno')
    busca_turma = _get_str('buscaTurma')

    # Join na turma apenas se precisar filtrar por turma/status/busca
    precisa_join_turma = (status_turma in ('ativas', 'finalizadas')) or bool(busca_turma)

    if precisa_join_turma:
        query = query.outerjoin(Turma, Turma.id == Aluno.turma_id)

        if status_turma == 'ativas':
            query = query.filter(Turma.data_fim.is_(None))
        elif status_turma == 'finalizadas':
            query = query.filter(Turma.data_fim.isnot(None))

        # ✅ Busca por turma: Turma.nome OU Aluno.turma (fallback)
        if busca_turma:
            like_turma = f"%{busca_turma}%"
            conds_turma = []
            if hasattr(Turma, 'nome'):
                conds_turma.append(Turma.nome.ilike(like_turma))
            if hasattr(Aluno, 'turma'):
                conds_turma.append(Aluno.turma.ilike(like_turma))
            if conds_turma:
                query = query.filter(or_(*conds_turma))

    # Curso
    if curso_id:
        try:
            query = query.filter(Aluno.curso_id == int(curso_id))
        except:
            pass

    # ✅ Busca aluno: nome OU CPF (com/sem máscara) OU matrícula
    if busca_aluno:
        texto = (busca_aluno or '').strip()
        like_txt = f"%{texto}%"
        dig = only_digits(texto)  # remove .-/ espaços etc

        conds = []

        # CPF
        if hasattr(Aluno, 'cpf') and dig:
            if len(dig) == 11:
                conds.append(Aluno.cpf == dig)  # exato
            else:
                conds.append(Aluno.cpf.ilike(f"%{dig}%"))  # parcial

        # Matrícula (se existir)
        if hasattr(Aluno, 'matricula'):
            if dig:
                conds.append(Aluno.matricula.ilike(f"%{dig}%"))
            conds.append(Aluno.matricula.ilike(like_txt))

        # Nome / Nome social / Nome completo
        if hasattr(Aluno, 'nome_social'):
            conds.append(Aluno.nome_social.ilike(like_txt))
        if hasattr(Aluno, 'nome_completo'):
            conds.append(Aluno.nome_completo.ilike(like_txt))
        if hasattr(Aluno, 'nome'):
            conds.append(Aluno.nome.ilike(like_txt))
        if hasattr(Aluno, 'sobrenome'):
            conds.append(Aluno.sobrenome.ilike(like_txt))

        if conds:
            query = query.filter(or_(*conds))

    return query


def nome_exibicao_aluno(aluno: Aluno) -> str:
    nome = ''
    if hasattr(aluno, 'nome_social') and aluno.nome_social:
        nome = aluno.nome_social
    elif hasattr(aluno, 'nome_completo') and aluno.nome_completo:
        nome = aluno.nome_completo
    elif hasattr(aluno, 'nome') and aluno.nome:
        if hasattr(aluno, 'sobrenome') and aluno.sobrenome:
            nome = f"{aluno.nome} {aluno.sobrenome}"
        else:
            nome = aluno.nome
    return (nome or '').strip()


def curso_nome_aluno(aluno: Aluno) -> str:
    # se tiver relacionamento: aluno.curso (objeto)
    if hasattr(aluno, 'curso') and aluno.curso:
        # pode ser string ou objeto
        if isinstance(aluno.curso, str):
            return aluno.curso
        if hasattr(aluno.curso, 'nome'):
            return aluno.curso.nome

    # fallback pelo curso_id
    if getattr(aluno, 'curso_id', None):
        c = Curso.query.get(aluno.curso_id)
        if c:
            return c.nome
    return "Sem curso"


def turma_nome_aluno(aluno: Aluno) -> str:
    # se tiver relacionamento: aluno.turma (objeto ou string)
    if hasattr(aluno, 'turma') and aluno.turma:
        if isinstance(aluno.turma, str):
            return aluno.turma
        if hasattr(aluno.turma, 'nome'):
            return aluno.turma.nome

    # fallback pelo turma_id
    if getattr(aluno, 'turma_id', None):
        t = Turma.query.get(aluno.turma_id)
        if t:
            return t.nome
    return "Sem turma"


# ==========================
# DASHBOARD
# ==========================
@dashboard_bp.route('', methods=['GET'])
def dashboard():
    try:
        # paginação (tabela)
        limit = max(1, min(_get_int('limit', 50), 500))
        offset = max(0, _get_int('offset', 0))

        # Query base
        base_q = db.session.query(Aluno)
        base_q = aplicar_filtros_alunos(base_q)

        # Subquery para contagem de ocorrências por aluno (evita N+1)
        occ_counts_sq = db.session.query(
            Ocorrencia.aluno_id.label('aluno_id'),
            func.count(Ocorrencia.id).label('qtd')
        ).group_by(Ocorrencia.aluno_id).subquery()

        # KPIs (filtrados)
        total_alunos = base_q.with_entities(func.count(Aluno.id)).scalar() or 0

        alunos_pcd = base_q.with_entities(func.count(Aluno.id)).filter(
            getattr(Aluno, 'pessoa_com_deficiencia') == True
        ).scalar() or 0

        # média idade (filtrada, ignorando NULL)
        idade_sum = base_q.with_entities(func.sum(Aluno.idade)).filter(Aluno.idade.isnot(None)).scalar() or 0
        idade_count = base_q.with_entities(func.count(Aluno.id)).filter(Aluno.idade.isnot(None)).scalar() or 0
        media_idade = round((idade_sum / idade_count), 1) if idade_count > 0 else 0

        # Turmas ativas/finalizadas (globais do sistema)
        turmas_ativas = db.session.query(func.count(Turma.id)).filter(Turma.data_fim.is_(None)).scalar() or 0
        turmas_finalizadas = db.session.query(func.count(Turma.id)).filter(Turma.data_fim.isnot(None)).scalar() or 0

        # Total de ocorrências (filtrado pelos alunos do filtro)
        alunos_ids_sq = base_q.with_entities(Aluno.id).subquery()
        total_ocorrencias = db.session.query(func.count(Ocorrencia.id)).filter(
            Ocorrencia.aluno_id.in_(db.session.query(alunos_ids_sq.c.id))
        ).scalar() or 0

        # ==========================
        # TABELA (limitada)
        # ==========================
        alunos_rows = (
            base_q
            .outerjoin(occ_counts_sq, occ_counts_sq.c.aluno_id == Aluno.id)
            .with_entities(Aluno, func.coalesce(occ_counts_sq.c.qtd, 0).label('ocorrencias'))
            .order_by(Aluno.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        alunos_filtrados_json = []
        for aluno, ocorrencias_count in alunos_rows:
            alunos_filtrados_json.append({
                'id': aluno.id,
                'nome': nome_exibicao_aluno(aluno),
                'turma': turma_nome_aluno(aluno),
                'curso': curso_nome_aluno(aluno),
                'idade': getattr(aluno, 'idade', None) or 0,
                'escola_integrada': getattr(aluno, 'escola_integrada', None) or 'Nenhuma',
                'pessoa_com_deficiencia': bool(getattr(aluno, 'pessoa_com_deficiencia', False)),
                'ocorrencias': int(ocorrencias_count or 0)
            })

        # ==========================
        # GRÁFICOS (FILTRADOS)
        # ==========================
        # 1) alunos por curso (inclui Sem Curso)
        alunos_por_curso = {}

        curso_counts = (
            base_q
            .with_entities(Aluno.curso_id, func.count(Aluno.id))
            .group_by(Aluno.curso_id)
            .all()
        )

        for curso_id, qtd in curso_counts:
            if curso_id is None:
                alunos_por_curso['Sem Curso'] = int(qtd or 0)
            else:
                c = Curso.query.get(curso_id)
                alunos_por_curso[(c.nome if c else f"Curso {curso_id}")] = int(qtd or 0)

        # 2) ocorrências por tipo (somente ocorrências dos alunos filtrados)
        ocorrencias_por_tipo = {}
        tipos = (
            db.session.query(Ocorrencia.tipo, func.count(Ocorrencia.id))
            .filter(Ocorrencia.aluno_id.in_(db.session.query(alunos_ids_sq.c.id)))
            .group_by(Ocorrencia.tipo)
            .all()
        )
        for tipo, qtd in tipos:
            ocorrencias_por_tipo[str(tipo or 'Não informado')] = int(qtd or 0)

        # 3) escolas integradas (filtrado)
        escolas_dict = {}
        escolas = (
            base_q
            .with_entities(Aluno.escola_integrada, func.count(Aluno.id))
            .group_by(Aluno.escola_integrada)
            .all()
        )
        for escola, qtd in escolas:
            escolas_dict[str(escola or 'Nenhuma')] = int(qtd or 0)

        return jsonify({
            'totalAlunos': total_alunos,
            'alunosPCD': alunos_pcd,
            'mediaIdade': media_idade,
            'turmasAtivas': turmas_ativas,
            'turmasFinalizadas': turmas_finalizadas,
            'totalOcorrencias': total_ocorrencias,
            'alunosFiltrados': alunos_filtrados_json,
            'graficos': {
                'alunosPorCurso': alunos_por_curso,
                'ocorrenciasPorTipo': ocorrencias_por_tipo,
                'escolas': escolas_dict
            },
            'mensagem': 'Dashboard carregado com filtros aplicados'
        }), 200

    except Exception as e:
        print(f"ERRO NO DASHBOARD: {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'totalAlunos': 0,
            'alunosPCD': 0,
            'mediaIdade': 0,
            'turmasAtivas': 0,
            'turmasFinalizadas': 0,
            'totalOcorrencias': 0,
            'alunosFiltrados': [],
            'graficos': {
                'alunosPorCurso': {},
                'ocorrenciasPorTipo': {},
                'escolas': {}
            },
            'mensagem': 'Dashboard em manutenção'
        }), 200


# ==========================
# EXPORT CSV (MESMOS FILTROS)
# ==========================
@dashboard_bp.route('/export', methods=['GET'])
def export_dashboard_csv():
    """
    Exporta CSV aplicando os mesmos filtros do dashboard.
    Sem limit/offset (exporta tudo dentro do filtro).
    """
    try:
        base_q = db.session.query(Aluno)
        base_q = aplicar_filtros_alunos(base_q)

        occ_counts_sq = db.session.query(
            Ocorrencia.aluno_id.label('aluno_id'),
            func.count(Ocorrencia.id).label('qtd')
        ).group_by(Ocorrencia.aluno_id).subquery()

        rows = (
            base_q
            .outerjoin(occ_counts_sq, occ_counts_sq.c.aluno_id == Aluno.id)
            .with_entities(Aluno, func.coalesce(occ_counts_sq.c.qtd, 0).label('ocorrencias'))
            .order_by(Aluno.id.asc())
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        writer.writerow(['ID','Nome','Turma','Curso','Idade','Escola Integrada','PCD','Ocorrências'])

        for aluno, ocorrencias_count in rows:
            writer.writerow([
                aluno.id,
                nome_exibicao_aluno(aluno),
                turma_nome_aluno(aluno),
                curso_nome_aluno(aluno),
                getattr(aluno, 'idade', None) or 0,
                getattr(aluno, 'escola_integrada', None) or 'Nenhuma',
                'Sim' if getattr(aluno, 'pessoa_com_deficiencia', False) else 'Não',
                int(ocorrencias_count or 0)
            ])

        csv_data = output.getvalue()
        output.close()

        filename = 'relatorio_dashboard.csv'

        return Response(
            '\ufeff' + csv_data,  # BOM para Excel
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ==========================
# DIAGNÓSTICO / TESTE / CURSOS
# ==========================
@dashboard_bp.route('/diagnostico', methods=['GET'])
def diagnostico():
    try:
        total_alunos = db.session.query(func.count(Aluno.id)).scalar() or 0
        total_turmas = db.session.query(func.count(Turma.id)).scalar() or 0
        total_cursos = db.session.query(func.count(Curso.id)).scalar() or 0
        total_ocorrencias = db.session.query(func.count(Ocorrencia.id)).scalar() or 0

        alunos_amostra = []
        for aluno in Aluno.query.limit(3).all():
            cpf = getattr(aluno, 'cpf', None)
            alunos_amostra.append({
                'id': aluno.id,
                'nome': getattr(aluno, 'nome', None),
                'cpf': (cpf[:3] + '***') if cpf else None,
                'tem_turma': getattr(aluno, 'turma_id', None) is not None,
                'tem_curso': getattr(aluno, 'curso_id', None) is not None
            })

        return jsonify({
            'status': 'OK',
            'totais': {
                'alunos': total_alunos,
                'turmas': total_turmas,
                'cursos': total_cursos,
                'ocorrencias': total_ocorrencias
            },
            'amostra_alunos': alunos_amostra,
            'mensagem': f'Sistema operacional com {total_alunos} alunos'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'ERRO',
            'erro': str(e),
            'mensagem': 'Problema na conexão com o banco'
        }), 500


@dashboard_bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'OK',
        'mensagem': 'Dashboard funcionando',
        'timestamp': 'teste'
    }), 200


@dashboard_bp.route('/aluno/<int:aluno_id>/ocorrencias', methods=['GET'])
def ocorrencias_por_aluno(aluno_id: int):
    try:
        aluno = Aluno.query.get(aluno_id)
        if not aluno:
            return jsonify({'erro': 'Aluno não encontrado'}), 404

        q = Ocorrencia.query.filter(Ocorrencia.aluno_id == aluno_id).order_by(Ocorrencia.data.desc())
        ocorrencias = q.all()

        return jsonify({
            'alunoId': aluno_id,
            'alunoNome': nome_exibicao_aluno(aluno),
            'total': len(ocorrencias),
            'ocorrencias': [o.to_dict() for o in ocorrencias]
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@dashboard_bp.route('/cursos-list', methods=['GET'])
def listar_cursos():
    try:
        cursos = Curso.query.order_by(Curso.nome).all()
        return jsonify([{'id': c.id, 'nome': c.nome} for c in cursos]), 200
    except Exception:
        return jsonify([{'id': 1, 'nome': 'Erro ao carregar'}]), 200
