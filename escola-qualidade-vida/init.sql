-- Criação do Banco de Dados
CREATE DATABASE IF NOT EXISTS `projetoteste` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_0900_ai_ci;

USE `projetoteste`;

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `senha` VARCHAR(255) NOT NULL,
  `tipo_usuario` ENUM('admin', 'professor', 'coordenador') NOT NULL DEFAULT 'professor',
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela de Cursos
CREATE TABLE IF NOT EXISTS `curso` (
  `id_curso` INT NOT NULL AUTO_INCREMENT,
  `nome_curso` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela de Turmas
CREATE TABLE IF NOT EXISTS `turma` (
  `id_turma` INT NOT NULL AUTO_INCREMENT,
  `nome_turma` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_turma`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela de Alunos
CREATE TABLE IF NOT EXISTS `aluno` (
  `id_aluno` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `turma_id` INT NOT NULL,
  `curso_id` INT NOT NULL,
  `periodo` ENUM('manhã', 'tarde', 'noite') NOT NULL,
  `imagem` VARCHAR(255) DEFAULT NULL,
  `nome_responsavel` VARCHAR(100) NOT NULL,
  `telefone_responsavel` VARCHAR(20) DEFAULT NULL,
  `celular_responsavel` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id_aluno`),
  KEY `turma_id` (`turma_id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `aluno_ibfk_1` FOREIGN KEY (`turma_id`) REFERENCES `turma` (`id_turma`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `aluno_ibfk_2` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id_curso`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela de Ocorrências (Corrigida)
CREATE TABLE IF NOT EXISTS `ocorrencia` (
  `id_ocorrencia` INT NOT NULL AUTO_INCREMENT,
  `aluno_id` INT NOT NULL,
  `usuario_id` INT NULL,
  `ocorrencia_tipo` ENUM('atestado', 'falta', 'ocorrencia') NOT NULL,
  `conteudo` TEXT NOT NULL,
  `data_ocorrencia` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_ocorrencia`),
  KEY `aluno_id` (`aluno_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `ocorrencia_ibfk_1` FOREIGN KEY (`aluno_id`) REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE,
  CONSTRAINT `ocorrencia_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabela de Avaliações
CREATE TABLE IF NOT EXISTS `avaliacoes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `aluno_id` INT NOT NULL,
  `satisfacao` INT NOT NULL CHECK (`satisfacao` BETWEEN 1 AND 5),
  `comentario` TEXT,
  PRIMARY KEY (`id`),
  KEY `aluno_id` (`aluno_id`),
  CONSTRAINT `avaliacoes_ibfk_1` FOREIGN KEY (`aluno_id`) REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dados Iniciais
INSERT INTO `usuarios` (`nome`, `email`, `senha`, `tipo_usuario`) VALUES
('Administrador', 'admin@escola.edu.br', SHA2('admin123', 256), 'admin'),
('Professora Ana', 'ana@escola.com', SHA2('ana123', 256), 'professor'),
('Coordenador Pedro', 'pedro@escola.com', SHA2('pedro456', 256), 'coordenador');

INSERT INTO `curso` (`nome_curso`) VALUES
('Ensino Fundamental'),
('Ensino Médio Regular'),
('Técnico em Informática');

INSERT INTO `turma` (`nome_turma`) VALUES
('1º Ano A'),
('2º Ano B'),
('3º Ano C');

INSERT INTO `aluno` (
  `nome`, `turma_id`, `curso_id`, `periodo`,
  `imagem`, `nome_responsavel`, `telefone_responsavel`, `celular_responsavel`
) VALUES
('Maria Oliveira', 1, 1, 'manhã', NULL, 'Carlos Oliveira', '(11) 9999-8888', '(11) 97777-6666'),
('João Silva', 2, 2, 'tarde', 'joao.jpg', 'Ana Silva', '(21) 8888-7777', '(21) 96666-5555'),
('Pedro Costa', 3, 3, 'noite', NULL, 'Fernanda Costa', '(31) 7777-6666', '(31) 95555-4444');

INSERT INTO `ocorrencia` (`aluno_id`, `usuario_id`, `ocorrencia_tipo`, `conteudo`) VALUES
(1, 2, 'falta', 'Falta não justificada'),
(2, 3, 'atestado', 'Atestado médico válido por 3 dias');

INSERT INTO `avaliacoes` (`aluno_id`, `satisfacao`, `comentario`) VALUES
(1, 5, 'Excelente desempenho'),
(2, 4, 'Bom desenvolvimento');

-- Usuário para aplicação
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'SenhaSegura123!';
GRANT SELECT, INSERT, UPDATE, DELETE ON `projetoteste`.* TO 'app_user'@'localhost';

-- Mensagem Final
SELECT 'Banco e dados iniciais configurados com sucesso!' AS Status;