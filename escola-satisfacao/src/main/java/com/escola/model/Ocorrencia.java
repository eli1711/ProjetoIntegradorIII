package com.escola.model;

import java.time.LocalDateTime;

public class Ocorrencia {
    private int idOcorrencia;
    private int alunoId;
    private String ocorrenciaTipo; // Pode ser "atestado", "falta" ou "ocorrencia"
    private String conteudo;
    private LocalDateTime dataOcorrencia;

    // Construtor vazio
    public Ocorrencia() {
    }

    // Construtor com todos os campos
    public Ocorrencia(int idOcorrencia, int alunoId, String ocorrenciaTipo, String conteudo, LocalDateTime dataOcorrencia) {
        this.idOcorrencia = idOcorrencia;
        this.alunoId = alunoId;
        this.ocorrenciaTipo = ocorrenciaTipo;
        this.conteudo = conteudo;
        this.dataOcorrencia = dataOcorrencia;
    }

    // Getters e Setters

    public int getIdOcorrencia() {
        return idOcorrencia;
    }

    public void setIdOcorrencia(int idOcorrencia) {
        this.idOcorrencia = idOcorrencia;
    }

    public int getAlunoId() {
        return alunoId;
    }

    public void setAlunoId(int alunoId) {
        this.alunoId = alunoId;
    }

    public String getOcorrenciaTipo() {
        return ocorrenciaTipo;
    }

    public void setOcorrenciaTipo(String ocorrenciaTipo) {
        this.ocorrenciaTipo = ocorrenciaTipo;
    }

    public String getConteudo() {
        return conteudo;
    }

    public void setConteudo(String conteudo) {
        this.conteudo = conteudo;
    }

    public LocalDateTime getDataOcorrencia() {
        return dataOcorrencia;
    }

    public void setDataOcorrencia(LocalDateTime dataOcorrencia) {
        this.dataOcorrencia = dataOcorrencia;
    }

    // Método toString para facilitar a visualização dos dados
    @Override
    public String toString() {
        return "Ocorrencia{" +
                "idOcorrencia=" + idOcorrencia +
                ", alunoId=" + alunoId +
                ", ocorrenciaTipo='" + ocorrenciaTipo + '\'' +
                ", conteudo='" + conteudo + '\'' +
                ", dataOcorrencia=" + dataOcorrencia +
                '}';
    }
}