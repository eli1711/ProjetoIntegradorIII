from flask import Flask, jsonify, request
from app.models.aluno import Aluno, db

app = Flask(__name__)

@app.route('/consultar/aluno', methods=['GET'])
def consultar_aluno():
    try:
        # Pegando o parâmetro 'id' ou 'nome' da query string
        aluno_id = request.args.get('id')
        aluno_nome = request.args.get('nome')

        # Verificando se o 'id' foi passado
        if aluno_id:
            aluno = Aluno.query.filter_by(id=aluno_id).first()
        elif aluno_nome:
            aluno = Aluno.query.filter_by(nome=aluno_nome).first()
        else:
            return jsonify({"erro": "É necessário informar um 'id' ou 'nome' para consulta."}), 400

        # Verifica se o aluno foi encontrado
        if aluno:
            return jsonify({
                "id": aluno.id,
                "nome": aluno.nome,
                "sobrenome": aluno.sobrenome,
                "cidade": aluno.cidade,
                "bairro": aluno.bairro,
                "rua": aluno.rua,
                "idade": aluno.idade,
                "responsavel_nome": aluno.nome_responsavel,
                "telefone_responsavel": aluno.telefone_responsavel,
                "imagem": aluno.imagem
            }), 200
        else:
            return jsonify({"erro": "Aluno não encontrado."}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
