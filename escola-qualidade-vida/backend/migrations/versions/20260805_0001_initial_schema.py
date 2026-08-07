"""initial schema

Revision ID: 20260805_0001
Revises:
Create Date: 2026-08-05 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260805_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    cargo_enum = sa.Enum("administrador", "coordenador", "analista", name="cargo_enum")
    cargo_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "cursos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )

    op.create_table(
        "empresa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "responsavel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome_completo", sa.String(length=255), nullable=False),
        sa.Column("parentesco", sa.String(length=255), nullable=False),
        sa.Column("telefone", sa.String(length=50), nullable=False),
        sa.Column("endereco", sa.String(length=255), nullable=True),
        sa.Column("cep", sa.String(length=8), nullable=True),
        sa.Column("bairro", sa.String(length=255), nullable=True),
        sa.Column("municipio", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("senha", sa.String(length=255), nullable=False),
        sa.Column("cargo", cargo_enum, nullable=False),
        sa.Column("token_recuperacao", sa.String(length=255), nullable=True),
        sa.Column("token_expiracao", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "turmas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("semestre", sa.String(length=1), nullable=False),
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("data_fim", sa.Date(), nullable=True),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_turmas_curso_id", "turmas", ["curso_id"])

    op.create_table(
        "aluno",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cpf", sa.String(length=14), nullable=False),
        sa.Column("nome_completo", sa.String(length=255), nullable=True),
        sa.Column("nome_social", sa.String(length=255), nullable=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("sobrenome", sa.String(length=255), nullable=False),
        sa.Column("matricula", sa.String(length=255), nullable=False),
        sa.Column("cidade", sa.String(length=255), nullable=False),
        sa.Column("bairro", sa.String(length=255), nullable=False),
        sa.Column("rua", sa.String(length=255), nullable=False),
        sa.Column("idade", sa.Integer(), nullable=False),
        sa.Column("empregado", sa.String(length=10), nullable=False),
        sa.Column("mora_com_quem", sa.String(length=255), nullable=True),
        sa.Column("sobre_aluno", sa.Text(), nullable=True),
        sa.Column("foto", sa.String(length=255), nullable=True),
        sa.Column("curso_id", sa.Integer(), nullable=True),
        sa.Column("turma_id", sa.Integer(), nullable=True),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("responsavel_id", sa.Integer(), nullable=True),
        sa.Column("telefone", sa.String(length=255), nullable=True),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("linha_atendimento", sa.String(length=10), nullable=False),
        sa.Column("curso", sa.String(length=255), nullable=True),
        sa.Column("turma", sa.String(length=255), nullable=True),
        sa.Column("data_inicio_curso", sa.Date(), nullable=True),
        sa.Column("empresa_contratante", sa.String(length=255), nullable=True),
        sa.Column("escola_integrada", sa.String(length=20), nullable=False),
        sa.Column("pessoa_com_deficiencia", sa.Boolean(), nullable=True),
        sa.Column("outras_informacoes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresa.id"]),
        sa.ForeignKeyConstraint(["responsavel_id"], ["responsavel.id"]),
        sa.ForeignKeyConstraint(["turma_id"], ["turmas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpf"),
        sa.UniqueConstraint("matricula"),
    )
    op.create_index("ix_aluno_curso_id", "aluno", ["curso_id"])
    op.create_index("ix_aluno_turma_id", "aluno", ["turma_id"])

    op.create_table(
        "ocorrencias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("data", sa.DateTime(), nullable=False),
        sa.Column("data_ocorrencia", sa.Date(), nullable=True),
        sa.Column("alerta_sensivel", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("alerta_sensivel_tipo", sa.String(length=50), nullable=True),
        sa.Column("alerta_sensivel_nivel", sa.String(length=20), nullable=True),
        sa.Column("alerta_sensivel_motivos", sa.Text(), nullable=True),
        sa.Column("acao_tomada", sa.Text(), nullable=True),
        sa.Column("acompanhamento", sa.Text(), nullable=True),
        sa.Column("data_acompanhamento", sa.Date(), nullable=True),
        sa.Column("status_acompanhamento", sa.String(length=30), nullable=False, server_default="nao_aplicavel"),
        sa.Column("turma_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["aluno_id"], ["aluno.id"]),
        sa.ForeignKeyConstraint(["turma_id"], ["turmas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ocorrencias_alerta_sensivel", "ocorrencias", ["alerta_sensivel"])
    op.create_index("ix_ocorrencias_aluno_id", "ocorrencias", ["aluno_id"])
    op.create_index("ix_ocorrencias_turma_id", "ocorrencias", ["turma_id"])


def downgrade():
    op.drop_index("ix_ocorrencias_turma_id", table_name="ocorrencias")
    op.drop_index("ix_ocorrencias_aluno_id", table_name="ocorrencias")
    op.drop_index("ix_ocorrencias_alerta_sensivel", table_name="ocorrencias")
    op.drop_table("ocorrencias")
    op.drop_index("ix_aluno_turma_id", table_name="aluno")
    op.drop_index("ix_aluno_curso_id", table_name="aluno")
    op.drop_table("aluno")
    op.drop_index("ix_turmas_curso_id", table_name="turmas")
    op.drop_table("turmas")
    op.drop_table("usuarios")
    op.drop_table("responsavel")
    op.drop_table("empresa")
    op.drop_table("cursos")
    sa.Enum(name="cargo_enum").drop(op.get_bind(), checkfirst=True)
