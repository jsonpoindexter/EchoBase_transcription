"""init

Revision ID: abb4f1071cf6
Revises: 
Create Date: 2025-07-14 23:35:52.069018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'abb4f1071cf6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('systems',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('api_key', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('api_key'),
    sa.UniqueConstraint('email')
    )
    op.create_table('radio_units',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('system_id', sa.Integer(), nullable=False),
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.Column('alias', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['system_id'], ['systems.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('system_id', 'unit_id', name='uq_system_unit')
    )
    op.create_table('talkgroups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('system_id', sa.Integer(), nullable=False),
    sa.Column('tg_number', sa.Integer(), nullable=False),
    sa.Column('alias', sa.String(length=100), nullable=True),
    sa.Column('whisper_prompt', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['system_id'], ['systems.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('system_id', 'tg_number', name='uq_system_tg')
    )
    op.create_table('calls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('system_id', sa.Integer(), nullable=False),
    sa.Column('talkgroup_id', sa.Integer(), nullable=True),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('duration', sa.Float(), nullable=True),
    sa.Column('audio_path', sa.String(length=255), nullable=False),
    sa.Column('transcript', sa.Text(), nullable=True),
    sa.Column('corrected_transcript', sa.Text(), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('needs_review', sa.Boolean(), nullable=False),
    sa.Column('transcriber', sa.String(length=100), nullable=True),
    sa.Column('reviewed_by', sa.Integer(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('transcript_tsv', postgresql.TSVECTOR(), nullable=True),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['system_id'], ['systems.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['talkgroup_id'], ['talkgroups.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['unit_id'], ['radio_units.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calls_talkgroup_timestamp', 'calls', ['talkgroup_id', 'timestamp'], unique=False)
    op.create_index(op.f('ix_calls_timestamp'), 'calls', ['timestamp'], unique=False)
    op.create_index('ix_calls_transcript_tsv', 'calls', ['transcript_tsv'], unique=False, postgresql_using='gin')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_calls_transcript_tsv', table_name='calls', postgresql_using='gin')
    op.drop_index(op.f('ix_calls_timestamp'), table_name='calls')
    op.drop_index('ix_calls_talkgroup_timestamp', table_name='calls')
    op.drop_table('calls')
    op.drop_table('talkgroups')
    op.drop_table('radio_units')
    op.drop_table('users')
    op.drop_table('systems')
    # ### end Alembic commands ###
