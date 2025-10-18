from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:senha@localhost/nome_do_banco'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definição do modelo Aluno
class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(10), nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)

# Definição do modelo Ocorrencia
class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_ocorrencia = db.Column(db.Date, nullable=False)

# Rota para buscar alunos com filtros
@consulta_aluno_bp.route('/alunos/buscar', methods=['GET'])
def buscar_alunos():
    nome = request.args.get('nome', '')
    matricula = request.args.get('matricula', '')
    turma = request.args.get('turma', '')
    periodo = request.args.get('periodo', '')

    query = Aluno.query

    if nome:
        query = query.filter(Aluno.nome.ilike(f'%{nome}%'))
    if matricula:
        query = query.filter(Aluno.matricula.ilike(f'%{matricula}%'))
    if turma:
        query = query.filter(Aluno.turma.ilike(f'%{turma}%'))
    if periodo:
        query = query.filter(Aluno.periodo.ilike(f'%{periodo}%'))

    alunos = query.all()

    if alunos:
        alunos_data = []
        for aluno in alunos:
            alunos_data.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'curso': aluno.curso.nome,  # Inclui o nome do curso
                'foto': aluno.foto
            })
        
        return jsonify(alunos_data)

    return jsonify({"erro": "Nenhum aluno encontrado."}), 404
