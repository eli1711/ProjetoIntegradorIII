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
        aluno_nome = request.args.get('aluno', '')
        turma_nome = request.args.get('turma', '')
        status_turma = request.args.get('status', 'ativas')

        print(f"Filtros recebidos: aluno={aluno_nome}, turma={turma_nome}, status={status_turma}")

        # 1. Calcular totais básicos
        total_alunos = Aluno.query.count()
        print(f"Total de alunos: {total_alunos}")
        
        # 2. Alunos PCD
        alunos_pcd = Aluno.query.filter_by(pessoa_com_deficiencia=True).count()
        print(f"Alunos PCD: {alunos_pcd}")
        
        # 3. Média de idade
        media_idade_result = db.session.query(func.avg(Aluno.idade)).scalar()
        media_idade = round(media_idade_result, 1) if media_idade_result else 0
        print(f"Média de idade: {media_idade}")
        
        # 4. Turmas Ativas e Finalizadas
        # Primeiro, verificar se a coluna 'ativa' existe no modelo Turma
        turmas_ativas = 0
        turmas_finalizadas = 0
        
        try:
            # Tentar filtrar por coluna 'ativa' se existir
            if hasattr(Turma, 'ativa'):
                turmas_ativas = Turma.query.filter_by(ativa=True).count()
                turmas_finalizadas = Turma.query.filter_by(ativa=False).count()
            else:
                # Se não existir, usar outra lógica
                turmas_ativas = Turma.query.count()
                turmas_finalizadas = 0
        except Exception as e:
            print(f"Erro ao contar turmas: {e}")
            turmas_ativas = Turma.query.count()
            turmas_finalizadas = 0
        
        print(f"Turmas ativas: {turmas_ativas}, turmas finalizadas: {turmas_finalizadas}")
        
        # 5. Total de Ocorrências
        total_ocorrencias = Ocorrencia.query.count()
        print(f"Total de ocorrências: {total_ocorrencias}")
        
        # 6. Buscar alunos com filtros
        query = Aluno.query
        
        if aluno_nome:
            query = query.filter(
                db.or_(
                    Aluno.nome.ilike(f'%{aluno_nome}%'),
                    Aluno.nome_completo.ilike(f'%{aluno_nome}%'),
                    Aluno.nome_social.ilike(f'%{aluno_nome}%')
                )
            )
        
        if turma_nome:
            query = query.filter(Aluno.turma.ilike(f'%{turma_nome}%'))
        
        # Filtrar por status da turma (se a relação existir)
        try:
            if status_turma == 'ativas' and hasattr(Turma, 'ativa'):
                # Usar join para filtrar turmas ativas
                query = query.join(Turma, Turma.id == Aluno.turma_id).filter(Turma.ativa == True)
            elif status_turma == 'finalizadas' and hasattr(Turma, 'ativa'):
                query = query.join(Turma, Turma.id == Aluno.turma_id).filter(Turma.ativa == False)
        except Exception as e:
            print(f"Erro ao filtrar por status da turma: {e}")
            # Continuar sem filtrar por status
        
        alunos_filtrados = query.all()
        print(f"Alunos filtrados encontrados: {len(alunos_filtrados)}")
        
        # 7. Dados para gráficos
        
        # Alunos por curso
        alunos_por_curso = {}
        alunos_todos = Aluno.query.all()
        for aluno in alunos_todos:
            curso_nome = aluno.curso or 'Sem Curso'
            if curso_nome not in alunos_por_curso:
                alunos_por_curso[curso_nome] = 0
            alunos_por_curso[curso_nome] += 1
        
        # Ocorrências por tipo
        ocorrencias_por_tipo = {}
        ocorrencias_todas = Ocorrencia.query.all()
        for ocor in ocorrencias_todas:
            tipo = ocor.tipo or 'Sem Tipo'
            if tipo not in ocorrencias_por_tipo:
                ocorrencias_por_tipo[tipo] = 0
            ocorrencias_por_tipo[tipo] += 1
        
        # Escolas integradas
        escolas = {}
        for aluno in alunos_todos:
            escola = aluno.escola_integrada or 'Nenhuma'
            if escola not in escolas:
                escolas[escola] = 0
            escolas[escola] += 1
        
        # 8. Preparar resposta com alunos filtrados
        alunos_filtrados_json = []
        for aluno in alunos_filtrados:
            # Contar ocorrências do aluno
            ocorrencias_aluno = Ocorrencia.query.filter_by(aluno_id=aluno.id).count() if hasattr(Ocorrencia, 'aluno_id') else 0
            
            alunos_filtrados_json.append({
                'id': aluno.id,
                'nome': aluno.nome_social or aluno.nome or aluno.nome_completo or '',
                'turma': aluno.turma or '',
                'curso': aluno.curso or '',
                'idade': aluno.idade or 0,
                'escola_integrada': aluno.escola_integrada or 'Nenhuma',
                'pessoa_com_deficiencia': bool(aluno.pessoa_com_deficiencia),
                'ocorrencias': ocorrencias_aluno
            })
        
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
                'escolas': escolas
            }
        }), 200
        
    except Exception as e:
        print(f"Erro grave no endpoint /dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'erro': f'Erro interno no servidor: {str(e)}',
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
            }
        }), 200  # Retornar 200 mesmo com erro para não quebrar o frontend

# Rota para debug - mostrar todos os alunos
@dashboard_bp.route('/debug', methods=['GET'])
def debug_alunos():
    try:
        alunos = Aluno.query.limit(10).all()
        resultado = []
        for aluno in alunos:
            resultado.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'nome_completo': aluno.nome_completo,
                'nome_social': aluno.nome_social,
                'turma': aluno.turma,
                'curso': aluno.curso,
                'idade': aluno.idade,
                'escola_integrada': aluno.escola_integrada,
                'pessoa_com_deficiencia': aluno.pessoa_com_deficiencia,
                'turma_id': aluno.turma_id,
                'curso_id': aluno.curso_id
            })
        return jsonify({
            'total': Aluno.query.count(),
            'amostra': resultado
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Rota para testar conexão
@dashboard_bp.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'OK',
        'mensagem': 'Endpoint dashboard funcionando',
        'alunos_total': Aluno.query.count() if hasattr(Aluno, 'query') else 'Modelo não carregado'
    }), 200