"""Add performance indexes

Revision ID: 002
Revises: 001
Create Date: 2025-07-08 22:05:02.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Document indexes
    op.create_index('idx_document_processed_created', 'document', ['processed', 'created_at'])
    op.create_index('idx_document_metadata_gin', 'document', ['metadata'], postgresql_using='gin')
    
    # Semantic block indexes
    op.create_index('idx_semantic_block_created', 'semantic_block', ['created_at'])
    op.create_index('idx_semantic_block_metadata_gin', 'semantic_block', ['metadata'], postgresql_using='gin')
    op.create_index('idx_semantic_block_content_gist', 'semantic_block', ['content'], postgresql_using='gist',
                    postgresql_ops={'content': 'gist_trgm_ops'})
    
    # Proposal indexes
    op.create_index('idx_proposal_created_status', 'proposal', ['created_at', 'status'])
    op.create_index('idx_proposal_parameters_gin', 'proposal', ['parameters'], postgresql_using='gin')
    op.create_index('idx_proposal_content_gin', 'proposal', ['content'], postgresql_using='gin')
    
    # Comment indexes
    op.create_index('idx_comment_user_created', 'comment', ['user_id', 'created_at'])
    
    # Version indexes
    op.create_index('idx_version_created', 'version', ['created_at'])

def downgrade() -> None:
    # Drop document indexes
    op.drop_index('idx_document_processed_created', table_name='document')
    op.drop_index('idx_document_metadata_gin', table_name='document')
    
    # Drop semantic block indexes
    op.drop_index('idx_semantic_block_created', table_name='semantic_block')
    op.drop_index('idx_semantic_block_metadata_gin', table_name='semantic_block')
    op.drop_index('idx_semantic_block_content_gist', table_name='semantic_block')
    
    # Drop proposal indexes
    op.drop_index('idx_proposal_created_status', table_name='proposal')
    op.drop_index('idx_proposal_parameters_gin', table_name='proposal')
    op.drop_index('idx_proposal_content_gin', table_name='proposal')
    
    # Drop comment indexes
    op.drop_index('idx_comment_user_created', table_name='comment')
    
    # Drop version indexes
    op.drop_index('idx_version_created', table_name='version')
