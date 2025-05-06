from flask import Flask, jsonify, request
from app.models.aluno import Aluno, db

app = Flask(__name__)

@app.route('/cadastro/aluno', methods=['POST'])
def cadastrar_aluno():
    try:
        # Coletando os dados do formulário
        nome = request.form['name']
        sobrenome = request.form['sobrenome']
        cidade = request.form['cidade']
        bairro = request.form['bairro']
        rua = request.form['rua']
        idade = request.form['idade']
        nome_responsavel = request.form.get('nomeResponsavel', '')
        telefone_responsavel = request.form.get('respSobrenome', '')
        celular_responsavel = request.form.get('respParentesco', '')

        # Processamento do arquivo de imagem
        imagem = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            filename = file.filename
            # Aqui você pode adicionar uma lógica para salvar o arquivo no servidor
            imagem = f"/uploads/{filename}"
            file.save(f"./static/uploads/{filename}")

        # Criando o aluno no banco
        novo_aluno = Aluno(
            nome=nome,
            sobrenome=sobrenome,
            cidade=cidade,
            bairro=bairro,
            rua=rua,
            idade=idade,
            nome_responsavel=nome_responsavel,
            telefone_responsavel=telefone_responsavel,
            celular_responsavel=celular_responsavel,
            imagem=imagem
        )

        db.session.add(novo_aluno)
        db.session.commit()

        return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao cadastrar o aluno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
