from flask import Blueprint, request, jsonify
from app import db
from app.models.ocorrencia import Ocorrencia
from app.models.aluno import Aluno
from app.models.turma import Turma
from datetime import datetime

ocorrencia_bp = Blueprint('ocorrencias', __name__, url_prefix='/ocorrencias')

@ocorrencia_bp.route('/tipos', methods=['GET'])
def listar_tipos():
    """Retorna a lista de tipos de ocorrência disponíveis"""
    try:
        tipos = Ocorrencia.get_tipos()
        return jsonify({'tipos': tipos}), 200
    except Exception as e:
        return jsonify({'erro': 'Erro ao listar tipos', 'detalhes': str(e)}), 500

@ocorrencia_bp.route('/', methods=['POST'])
def cadastrar_ocorrencia():
    """Cadastra uma nova ocorrência"""
    try:
        dados = request.get_json()
        
        # Validações básicas
        if not dados.get('aluno_id'):
            return jsonify({'erro': 'ID do aluno é obrigatório'}), 400
        
        if not dados.get('tipo'):
            return jsonify({'erro': 'Tipo de ocorrência é obrigatório'}), 400
            
        if not dados.get('descricao'):
            return jsonify({'erro': 'Descrição é obrigatória'}), 400
        
        # Busca o aluno para obter a turma_id
        aluno = Aluno.query.get(dados['aluno_id'])
        if not aluno:
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        # Verifica se o aluno tem turma
        if not aluno.turma_id:
            return jsonify({'erro': 'Aluno não está vinculado a uma turma'}), 400
        
        # Verifica se o tipo é válido
        tipo = dados['tipo']
        tipos_validos = Ocorrencia.get_tipos()
        if tipo not in tipos_validos:
            return jsonify({'erro': f'Tipo inválido. Tipos válidos: {", ".join(tipos_validos)}'}), 400
        
        # Converte data_ocorrencia se fornecida
        data_ocorrencia = None
        if dados.get('data_ocorrencia'):
            try:
                data_ocorrencia = datetime.strptime(dados['data_ocorrencia'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Cria a nova ocorrência
        nova_ocorrencia = Ocorrencia(
            aluno_id=dados['aluno_id'],
            tipo=tipo,
            descricao=dados['descricao'],
            data_ocorrencia=data_ocorrencia,
            turma_id=aluno.turma_id
        )
        
        db.session.add(nova_ocorrencia)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Ocorrência cadastrada com sucesso',
            'ocorrencia_id': nova_ocorrencia.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar ocorrência', 'detalhes': str(e)}), 500

@ocorrencia_bp.route('/', methods=['GET'])
def listar_todas_ocorrencias():
    """Lista todas as ocorrências com filtros opcionais"""
    aluno_id = request.args.get('aluno_id')
    turma_id = request.args.get('turma_id')
    tipo = request.args.get('tipo')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    try:
        query = Ocorrencia.query
        
        # Aplicar filtros
        if aluno_id:
            query = query.filter_by(aluno_id=aluno_id)
        
        if turma_id:
            query = query.filter_by(turma_id=turma_id)
            
        if tipo:
            query = query.filter_by(tipo=tipo)
            
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Ocorrencia.data_ocorrencia >= data_inicio_dt)
            except ValueError:
                return jsonify({'erro': 'Formato de data_inicio inválido. Use YYYY-MM-DD'}), 400
            
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
                query = query.filter(Ocorrencia.data_ocorrencia <= data_fim_dt)
            except ValueError:
                return jsonify({'erro': 'Formato de data_fim inválido. Use YYYY-MM-DD'}), 400

        ocorrencias = query.order_by(Ocorrencia.data.desc()).all()

        resultado = []
        for oc in ocorrencias:
            resultado.append(oc.to_dict())

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'erro': 'Erro ao listar ocorrências', 'detalhes': str(e)}), 500

@ocorrencia_bp.route('/<int:id>', methods=['GET'])
def obter_ocorrencia(id):
    """Obtém uma ocorrência específica"""
    try:
        ocorrencia = Ocorrencia.query.get_or_404(id)
        return jsonify(ocorrencia.to_dict()), 200
        
    except Exception as e:
        return jsonify({'erro': 'Ocorrência não encontrada', 'detalhes': str(e)}), 404

@ocorrencia_bp.route('/<int:id>', methods=['PUT'])
def atualizar_ocorrencia(id):
    """Atualiza uma ocorrência existente"""
    try:
        ocorrencia = Ocorrencia.query.get_or_404(id)
        dados = request.get_json()
        
        # Validações
        if dados.get('tipo') and dados['tipo'] not in Ocorrencia.get_tipos():
            return jsonify({'erro': 'Tipo de ocorrência inválido'}), 400
        
        # Atualiza os campos
        if 'tipo' in dados:
            ocorrencia.tipo = dados['tipo']
        
        if 'descricao' in dados:
            ocorrencia.descricao = dados['descricao']
        
        if 'data_ocorrencia' in dados:
            if dados['data_ocorrencia']:
                ocorrencia.data_ocorrencia = datetime.strptime(dados['data_ocorrencia'], '%Y-%m-%d').date()
            else:
                ocorrencia.data_ocorrencia = None
        
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Ocorrência atualizada com sucesso',
            'ocorrencia': ocorrencia.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao atualizar ocorrência', 'detalhes': str(e)}), 500

@ocorrencia_bp.route('/<int:id>', methods=['DELETE'])
def excluir_ocorrencia(id):
    """Exclui uma ocorrência"""
    try:
        ocorrencia = Ocorrencia.query.get_or_404(id)
        
        db.session.delete(ocorrencia)
        db.session.commit()
        
        return jsonify({'mensagem': 'Ocorrência excluída com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao excluir ocorrência', 'detalhes': str(e)}), 500