"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-07-08 22:00:17.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE block_type AS ENUM ('title', 'client', 'context', 'problem', 'solution', 'scope', 'timeline', 'investment', 'differentials', 'cases')")
    op.execute("CREATE TYPE proposal_status AS ENUM ('draft', 'review', 'approved', 'rejected')")
    
    # Create documents table
    op.create_table(
        'document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create semantic blocks table
    op.create_table(
        'semantic_block',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('block_type', sa.Enum('title', 'client', 'context', 'problem', 'solution', 'scope', 'timeline', 'investment', 'differentials', 'cases', name='block_type'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('position', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['document_id'], ['document.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create proposals table
    op.create_table(
        'proposal',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('client_name', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'review', 'approved', 'rejected', name='proposal_status'), nullable=False, server_default='draft'),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create comments table
    op.create_table(
        'comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposal.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create versions table
    op.create_table(
        'version',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposal.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('proposal_id', 'version_number', name='uq_version_proposal_number')
    )
    
    # Create indexes
    op.create_index(op.f('ix_document_created_at'), 'document', ['created_at'], unique=False)
    op.create_index(op.f('ix_semantic_block_document_id'), 'semantic_block', ['document_id'], unique=False)
    op.create_index(op.f('ix_semantic_block_block_type'), 'semantic_block', ['block_type'], unique=False)
    op.create_index(op.f('ix_proposal_client_name'), 'proposal', ['client_name'], unique=False)
    op.create_index(op.f('ix_proposal_status'), 'proposal', ['status'], unique=False)
    op.create_index(op.f('ix_comment_proposal_id'), 'comment', ['proposal_id'], unique=False)
    op.create_index(op.f('ix_version_proposal_id'), 'version', ['proposal_id'], unique=False)

def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_version_proposal_id'), table_name='version')
    op.drop_index(op.f('ix_comment_proposal_id'), table_name='comment')
    op.drop_index(op.f('ix_proposal_status'), table_name='proposal')
    op.drop_index(op.f('ix_proposal_client_name'), table_name='proposal')
    op.drop_index(op.f('ix_semantic_block_block_type'), table_name='semantic_block')
    op.drop_index(op.f('ix_semantic_block_document_id'), table_name='semantic_block')
    op.drop_index(op.f('ix_document_created_at'), table_name='document')
    
    # Drop tables
    op.drop_table('version')
    op.drop_table('comment')
    op.drop_table('proposal')
    op.drop_table('semantic_block')
    op.drop_table('document')
    
    # Drop enum types
    op.execute('DROP TYPE proposal_status')
    op.execute('DROP TYPE block_type')
