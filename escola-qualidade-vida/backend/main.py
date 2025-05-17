import os
import time
from flask import Flask, request, redirect, url_for
from app import create_app, db
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from app.models.aluno import Aluno  # Certifique-se de importar a classe Aluno

# Criando a aplicação Flask
app = create_app()

def wait_for_db():
    """Espera até que o banco de dados esteja disponível."""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(db_uri)
    attempt = 0
    while True:
        try:
            with engine.connect():
                print("Conexão bem-sucedida com o banco de dados!")
                break
        except OperationalError:
            attempt += 1
            backoff_time = 2 ** attempt
            print(f"Banco de dados não disponível, tentando novamente em {backoff_time} segundos...")
            time.sleep(backoff_time)

# Função para cadastrar aluno
@app.route('/cadastrar-aluno', methods=['POST'])
def cadastrar_aluno():
    if request.method == 'POST':
        # Captura os dados do formulário
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        cidade = request.form['cidade']
        bairro = request.form['bairro']
        rua = request.form['rua']
        idade = request.form['idade']
        empregado = request.form['empregado']
        mora_com_quem = request.form['mora_com_quem']  # Corrigido o nome da variável
        sobre_aluno = request.form['sobre_aluno']
        
        # Processando o upload da foto
        foto = request.files['foto']
        foto_filename = None
        if foto:
            foto_filename = foto.filename
            if not os.path.exists('./uploads'):
                os.makedirs('./uploads')  # Cria o diretório de uploads, se necessário
            foto.save(f'./uploads/{foto_filename}')  # Salva a foto no diretório de uploads

        # Criando o objeto aluno
        novo_aluno = Aluno(
            nome=nome, sobrenome=sobrenome, cidade=cidade, bairro=bairro, rua=rua, 
            idade=idade, empregado=empregado, coma_com_quem=mora_com_quem, sobre_aluno=sobre_aluno, foto=foto_filename
        )

        # Adicionando o aluno ao banco de dados
        db.session.add(novo_aluno)
        db.session.commit()

        # Redirecionando para uma página de confirmação ou outra página
        return redirect(url_for('sucesso'))
# Rota de Sucesso
@app.route('/sucesso')
def sucesso():
    return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 200


# Aguarda disponibilidade do DB e cria tabelas
with app.app_context():
    wait_for_db()  # Espera até o banco de dados estar disponível
    db.create_all()  # Cria todas as tabelas

# Iniciando a aplicação
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
