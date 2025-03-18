CREATE DATABASE IF NOT EXISTS escola_db;

USE escola_db;

CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE avaliacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT,
    satisfacao INT,
    comentario TEXT,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);