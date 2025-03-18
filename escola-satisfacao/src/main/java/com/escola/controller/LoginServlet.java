package com.escola.controller;

import com.escola.dao.AlunoDAO;
import com.escola.model.Aluno;
import com.fasterxml.jackson.databind.ObjectMapper;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebServlet("/login")
public class LoginServlet extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String email = req.getParameter("email");
        String senha = req.getParameter("senha");

        AlunoDAO alunoDAO = new AlunoDAO();
        Aluno aluno = alunoDAO.login(email, senha);

        resp.setContentType("application/json");
        ObjectMapper mapper = new ObjectMapper();
        if (aluno != null) {
            mapper.writeValue(resp.getWriter(), aluno);
        } else {
            resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            mapper.writeValue(resp.getWriter(), "Email ou senha incorretos!");
        }
    }
}