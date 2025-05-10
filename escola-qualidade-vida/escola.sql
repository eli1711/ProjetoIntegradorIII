-- Criando o banco de dados
CREATE DATABASE IF NOT EXISTS escola_db;

-- Selecionando o banco de dados
USE escola_db;

-- Criando a tabela Aluno
CREATE TABLE IF NOT EXISTS Aluno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sobrenome VARCHAR(255) NOT NULL,
    cidade VARCHAR(255) NOT NULL,
    bairro VARCHAR(255) NOT NULL,
    rua VARCHAR(255) NOT NULL,
    idade INT NOT NULL,
    empregado ENUM('sim', 'não') NOT NULL,
    coma_com_quem VARCHAR(255),
    comorbidade TEXT,
    foto BLOB
);

-- Criando a tabela Responsavel_por_aluno
CREATE TABLE IF NOT EXISTS Responsavel_por_aluno (
    id_do_responsavel INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sobrenome VARCHAR(255) NOT NULL,
    grau_de_parentesco VARCHAR(255) NOT NULL,
    cidade VARCHAR(255) NOT NULL,
    bairro VARCHAR(255) NOT NULL,
    rua VARCHAR(255) NOT NULL,
    id_aluno INT,
    FOREIGN KEY (id_aluno) REFERENCES Aluno(id)
);
