# dashboard.py/ routers
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.extensions import db
from app.models.aluno import Aluno
from app.models.ocorrencia import Ocorrencia
from app.models.turma import Turma
from app.models.curso import Curso

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('', methods=['GET'])
def dashboard():
    try:
        print("=== DASHBOARD INICIADO ===")
        
        # 1. Totais básicos - USANDO CONSULTAS SIMPLES
        total_alunos = db.session.query(func.count(Aluno.id)).scalar() or 0
        print(f"Total de alunos: {total_alunos}")
        
        # 2. Alunos PCD
        alunos_pcd = db.session.query(func.count(Aluno.id)).filter(
            Aluno.pessoa_com_deficiencia == True
        ).scalar() or 0
        print(f"Alunos PCD: {alunos_pcd}")
        
        # 3. Média de idade - forma segura
        idade_soma = db.session.query(func.sum(Aluno.idade)).scalar() or 0
        count_com_idade = db.session.query(func.count(Aluno.id)).filter(
            Aluno.idade.isnot(None)
        ).scalar() or 1  # evitar divisão por zero
        media_idade = round(idade_soma / count_com_idade, 1) if count_com_idade > 0 else 0
        print(f"Média de idade: {media_idade}")
        
        # 4. Turmas Ativas e Finalizadas - CONSULTA SIMPLES
        todas_turmas = Turma.query.all()
        turmas_ativas = 0
        turmas_finalizadas = 0
        
        for turma in todas_turmas:
            if turma.data_fim is None:
                turmas_ativas += 1
            else:
                turmas_finalizadas += 1
        
        print(f"Turmas: {len(todas_turmas)} (Ativas: {turmas_ativas}, Finalizadas: {turmas_finalizadas})")
        
        # 5. Total de Ocorrências - CONSULTA SIMPLES
        total_ocorrencias = db.session.query(func.count(Ocorrencia.id)).scalar() or 0
        print(f"Total de ocorrências: {total_ocorrencias}")
        
        # 6. Buscar ALGUNS alunos (não todos de uma vez)
        alunos_limitados = Aluno.query.limit(50).all()
        print(f"Alunos carregados para tabela: {len(alunos_limitados)}")
        
        # 7. Dados para gráficos - FORMA SIMPLES
        # Alunos por curso
        alunos_por_curso = {}
        cursos = Curso.query.all()
        for curso in cursos:
            count = db.session.query(func.count(Aluno.id)).filter(
                Aluno.curso_id == curso.id
            ).scalar() or 0
            if count > 0:
                alunos_por_curso[curso.nome] = count
        
        # Se nenhum curso, adicionar alunos sem curso
        alunos_sem_curso = total_alunos - sum(alunos_por_curso.values())
        if alunos_sem_curso > 0:
            alunos_por_curso['Sem Curso'] = alunos_sem_curso
        
        # Ocorrências por tipo - FORMA SIMPLES
        ocorrencias_por_tipo = {}
        tipos_ocorrencias = db.session.query(
            Ocorrencia.tipo,
            func.count(Ocorrencia.id)
        ).group_by(Ocorrencia.tipo).all()
        
        for tipo, count in tipos_ocorrencias:
            ocorrencias_por_tipo[tipo] = count
        
        # Escolas integradas - FORMA SIMPLES
        escolas_dict = {}
        escolas_query = db.session.query(
            Aluno.escola_integrada,
            func.count(Aluno.id)
        ).group_by(Aluno.escola_integrada).all()
        
        for escola, count in escolas_query:
            escolas_dict[escola or 'Nenhuma'] = count
        
        # 8. Preparar resposta com alunos
        alunos_filtrados_json = []
        for aluno in alunos_limitados:
            # Contar ocorrências - forma segura
            ocorrencias_count = db.session.query(func.count(Ocorrencia.id)).filter(
                Ocorrencia.aluno_id == aluno.id
            ).scalar() or 0
            
            # Nome para exibição
            nome_exibicao = aluno.nome_social or aluno.nome or aluno.nome_completo or ""
            if not nome_exibicao and aluno.nome and aluno.sobrenome:
                nome_exibicao = f"{aluno.nome} {aluno.sobrenome}"
            
            # Nome do curso
            curso_nome = "Sem curso"
            if aluno.curso:
                curso_nome = aluno.curso
            elif aluno.curso_id:
                curso = Curso.query.get(aluno.curso_id)
                if curso:
                    curso_nome = curso.nome
            
            # Nome da turma
            turma_nome = "Sem turma"
            if aluno.turma:
                turma_nome = aluno.turma
            elif aluno.turma_id:
                turma = Turma.query.get(aluno.turma_id)
                if turma:
                    turma_nome = turma.nome
            
            alunos_filtrados_json.append({
                'id': aluno.id,
                'nome': nome_exibicao.strip(),
                'turma': turma_nome,
                'curso': curso_nome,
                'idade': aluno.idade or 0,
                'escola_integrada': aluno.escola_integrada or 'Nenhuma',
                'pessoa_com_deficiencia': bool(aluno.pessoa_com_deficiencia),
                'ocorrencias': ocorrencias_count
            })
        
        print(f"=== DASHBOARD FINALIZADO ===")
        
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
            }
        }), 200
        
    except Exception as e:
        print(f"ERRO NO DASHBOARD: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retornar resposta vazia mas funcional
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

# Rota SIMPLES para diagnóstico
@dashboard_bp.route('/diagnostico', methods=['GET'])
def diagnostico():
    """Endpoint simples para diagnóstico"""
    try:
        # Testes básicos
        total_alunos = db.session.query(func.count(Aluno.id)).scalar() or 0
        total_turmas = db.session.query(func.count(Turma.id)).scalar() or 0
        total_cursos = db.session.query(func.count(Curso.id)).scalar() or 0
        total_ocorrencias = db.session.query(func.count(Ocorrencia.id)).scalar() or 0
        
        # Pegar alguns alunos
        alunos_amostra = []
        for aluno in Aluno.query.limit(3).all():
            alunos_amostra.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'cpf': aluno.cpf[:3] + '***' if aluno.cpf else None,
                'tem_turma': aluno.turma_id is not None,
                'tem_curso': aluno.curso_id is not None
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

# Rota SIMPLES para testar
@dashboard_bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'OK',
        'mensagem': 'Dashboard funcionando',
        'timestamp': 'teste'
    }), 200

# Rota SIMPLES para listar cursos
@dashboard_bp.route('/cursos-list', methods=['GET'])
def listar_cursos():
    try:
        cursos = Curso.query.order_by(Curso.nome).all()
        return jsonify([{'id': c.id, 'nome': c.nome} for c in cursos]), 200
    except Exception as e:
        return jsonify([{'id': 1, 'nome': 'Erro ao carregar'}]), 200