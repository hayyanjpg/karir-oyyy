"""Initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("google_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("token_version", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_login",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("google_id", name="uq_users_google_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "job_applications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_name", sa.String(length=150), nullable=False),
        sa.Column("position_title", sa.String(length=150), nullable=False),
        sa.Column(
            "job_portal",
            sa.String(length=100),
            server_default=sa.text("'Lainnya'"),
            nullable=False,
        ),
        sa.Column(
            "work_model",
            sa.String(length=50),
            server_default=sa.text("'WFO'"),
            nullable=False,
        ),
        sa.Column("salary_range", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            server_default=sa.text("'Applied'"),
            nullable=False,
        ),
        sa.Column("applied_date", sa.Date(), nullable=False),
        sa.Column("job_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "work_model IN ('WFO', 'Hybrid', 'Remote')",
            name="chk_work_model",
        ),
        sa.CheckConstraint(
            "status IN ('Applied', 'Screening', 'Technical Test', 'HR Interview', "
            "'User Interview', 'Offering', 'Rejected', 'Ghosted')",
            name="chk_status",
        ),
        sa.CheckConstraint(
            "job_portal IN ('LinkedIn', 'Glints', 'JobStreet', 'Kalibrr', "
            "'Website Perusahaan', 'Lainnya')",
            name="chk_job_portal",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "application_status_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["job_applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_job_applications_user_applied",
        "job_applications",
        ["user_id", "applied_date"],
    )
    op.create_index(
        "ix_job_applications_user_status",
        "job_applications",
        ["user_id", "status"],
    )
    op.create_index(
        "ix_job_applications_user_work_model",
        "job_applications",
        ["user_id", "work_model"],
    )
    op.create_index(
        "ix_status_history_user_to_status",
        "application_status_history",
        ["user_id", "to_status"],
    )
    op.create_index(
        "ix_status_history_application_changed",
        "application_status_history",
        ["application_id", "changed_at"],
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_job_applications_updated_at
        BEFORE UPDATE ON job_applications
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_job_applications_updated_at ON job_applications;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    op.drop_index(
        "ix_status_history_application_changed",
        table_name="application_status_history",
    )
    op.drop_index(
        "ix_status_history_user_to_status",
        table_name="application_status_history",
    )
    op.drop_table("application_status_history")

    op.drop_index(
        "ix_job_applications_user_work_model",
        table_name="job_applications",
    )
    op.drop_index("ix_job_applications_user_status", table_name="job_applications")
    op.drop_index("ix_job_applications_user_applied", table_name="job_applications")
    op.drop_table("job_applications")

    op.drop_table("users")
