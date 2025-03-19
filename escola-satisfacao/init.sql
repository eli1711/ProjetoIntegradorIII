-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS `projetoteste` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `projetoteste`;

-- Tabela `curso`
CREATE TABLE IF NOT EXISTS `curso` (
  `id_curso` int NOT NULL AUTO_INCREMENT,
  `nome_curso` varchar(100) NOT NULL,
  PRIMARY KEY (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela `turma`
CREATE TABLE IF NOT EXISTS `turma` (
  `id_turma` int NOT NULL AUTO_INCREMENT,
  `nome_turma` varchar(50) NOT NULL,
  PRIMARY KEY (`id_turma`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela `aluno`
CREATE TABLE IF NOT EXISTS `aluno` (
  `id_aluno` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `turma_id` int NOT NULL,
  `curso_id` int NOT NULL,
  `periodo` enum('manhã','tarde','noite') NOT NULL,
  `imagem` varchar(255) DEFAULT NULL,
  `nome_responsavel` varchar(100) NOT NULL,
  `telefone_responsavel` varchar(20) DEFAULT NULL,
  `celular_responsavel` varchar(20) NOT NULL,
  PRIMARY KEY (`id_aluno`),
  KEY `turma_id` (`turma_id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `aluno_ibfk_1` FOREIGN KEY (`turma_id`) REFERENCES `turma` (`id_turma`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `aluno_ibfk_2` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id_curso`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela `ocorrencia`
CREATE TABLE IF NOT EXISTS `ocorrencia` (
  `id_ocorrencia` int NOT NULL AUTO_INCREMENT,
  `aluno_id` int NOT NULL,
  `ocorrencia_tipo` enum('atestado','falta','ocorrencia') NOT NULL,
  `conteudo` text NOT NULL,
  `data_ocorrencia` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_ocorrencia`),
  KEY `aluno_id` (`aluno_id`),
  CONSTRAINT `ocorrencia_ibfk_1` FOREIGN KEY (`aluno_id`) REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela `alunos` (original do escola_db)
CREATE TABLE IF NOT EXISTS `alunos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL UNIQUE,
  `senha` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela `avaliacoes` (original do escola_db)
CREATE TABLE IF NOT EXISTS `avaliacoes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `aluno_id` int NOT NULL,
  `satisfacao` int NOT NULL,
  `comentario` text,
  PRIMARY KEY (`id`),
  KEY `aluno_id` (`aluno_id`),
  CONSTRAINT `avaliacoes_ibfk_1` FOREIGN KEY (`aluno_id`) REFERENCES `alunos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;