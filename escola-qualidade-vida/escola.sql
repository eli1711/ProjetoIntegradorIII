-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS escola_db;
USE escola_db;

-- Tabela Empresa
CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    endereco VARCHAR(255),
    telefone VARCHAR(50),
    cidade VARCHAR(255),
    bairro VARCHAR(255),
    rua VARCHAR(255)
);

-- Tabela Responsavel
CREATE TABLE responsavel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sobrenome VARCHAR(255) NOT NULL,
    parentesco VARCHAR(255),
    telefone VARCHAR(50),
    cidade VARCHAR(255),
    bairro VARCHAR(255),
    rua VARCHAR(255)
);

-- Tabela usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(512) NOT NULL  -- Aumentado o tamanho para acomodar o hash de senha
    ALTER TABLE usuarios ADD COLUMN cargo VARCHAR(50) NOT NULL DEFAULT 'coordenador';
);

-- Tabela Aluno
CREATE TABLE aluno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sobrenome VARCHAR(255) NOT NULL,
    cidade VARCHAR(255) NOT NULL,
    bairro VARCHAR(255) NOT NULL,
    rua VARCHAR(255) NOT NULL,
    idade INT NOT NULL,
    empregado ENUM('sim','no') NOT NULL,
    mora_com_quem VARCHAR(255), 
    sobre_aluno TEXT,  -- 'Sobre o Aluno' é o campo principal, antes chamado de 'descricao_comorbidade'
    comorbidade TEXT,  -- 'Comorbidade' permanece para guardar detalhes relacionados à saúde
    foto VARCHAR(512),  -- Aumentado o tamanho do campo para acomodar caminhos de fotos maiores
    responsavel_id INT,
    empresa_id INT,
    FOREIGN KEY (responsavel_id) REFERENCES responsavel(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (empresa_id) REFERENCES empresa(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Tabela ocorrencias
CREATE TABLE ocorrencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    usuario_id INT,
    FOREIGN KEY (aluno_id) REFERENCES aluno(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Inserção de dados na tabela usuarios
INSERT INTO usuarios (id, nome, email, senha, cargo) VALUES
(3, 'Eli', 'teste@teste.com', 'pbkdf2:sha256:1000000$0UEjXz4l8io6nCvF$d8454aec349e258788f491b54d199029ffcd3cecf19d9d8e50bf73ce39ed1e12', 'coordenador');
