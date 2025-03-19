package com.escola.dao;

import com.escola.model.Aluno;
import com.escola.util.DatabaseUtil;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class AlunoDAO {

    public Aluno login(String email, String senha) {
        // Verifica se email ou senha são nulos
        if (email == null || senha == null) {
            return null;
        }

        // Consulta SQL para buscar o aluno na tabela `aluno`
        String sql = "SELECT * FROM aluno WHERE email = ? AND senha = ?";
        
        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            // Define os parâmetros da consulta
            stmt.setString(1, email);
            stmt.setString(2, senha);

            // Executa a consulta
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    // Cria um objeto Aluno e preenche com os dados do banco
                    Aluno aluno = new Aluno();
                    aluno.setIdAluno(rs.getInt("id_aluno"));
                    aluno.setNome(rs.getString("nome"));
                    aluno.setEmail(rs.getString("email"));
                    aluno.setSenha(rs.getString("senha")); // Evite armazenar a senha em texto puro no futuro
                    aluno.setTurmaId(rs.getInt("turma_id"));
                    aluno.setCursoId(rs.getInt("curso_id"));
                    aluno.setPeriodo(rs.getString("periodo"));
                    aluno.setImagem(rs.getString("imagem"));
                    aluno.setNomeResponsavel(rs.getString("nome_responsavel"));
                    aluno.setTelefoneResponsavel(rs.getString("telefone_responsavel"));
                    aluno.setCelularResponsavel(rs.getString("celular_responsavel"));
                    return aluno;
                }
            }
        } catch (SQLException e) {
            // Log do erro (em produção, use um framework de logging como SLF4J)
            System.out.println("Erro ao executar a consulta de login: " + e.getMessage());
            e.printStackTrace();
        }

        // Retorna null se o login falhar
        return null;
    }
}