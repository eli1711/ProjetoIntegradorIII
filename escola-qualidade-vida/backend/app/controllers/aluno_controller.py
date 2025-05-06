@router.get("/consultar")
async def consultar_alunos():
    alunos = db.query(Aluno).all()
    return {"alunos": alunos}
