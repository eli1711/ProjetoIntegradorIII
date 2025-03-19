package com.escola.dao;

import com.escola.model.Ocorrencia;
import com.escola.util.DatabaseUtil;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;

public class OcorrenciaDAO {

    // Método para inserir uma nova ocorrência
    public boolean inserirOcorrencia(Ocorrencia ocorrencia) {
        String sql = "INSERT INTO ocorrencia (aluno_id, ocorrencia_tipo, conteudo, data_ocorrencia) VALUES (?, ?, ?, ?)";
        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setInt(1, ocorrencia.getAlunoId());
            stmt.setString(2, ocorrencia.getOcorrenciaTipo());
            stmt.setString(3, ocorrencia.getConteudo());
            stmt.setObject(4, ocorrencia.getDataOcorrencia());

            int rowsAffected = stmt.executeUpdate();
            return rowsAffected > 0; // Retorna true se a ocorrência foi inserida com sucesso
        } catch (SQLException e) {
            System.out.println("Erro ao inserir ocorrência: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    // Outros métodos (buscar, atualizar, excluir) podem ser implementados aqui
}