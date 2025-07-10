"""Test database migrations."""
import pytest
from alembic.command import upgrade, downgrade
from alembic.config import Config
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from typing import List

def test_migrations_apply_successfully(alembic_config: Config, get_revisions: List[str]):
    """Test that all migrations can be applied successfully."""
    for revision in get_revisions:
        upgrade(alembic_config, revision)

def test_migrations_rollback_successfully(alembic_config: Config, get_revisions: List[str]):
    """Test that all migrations can be rolled back successfully."""
    # First upgrade to latest
    upgrade(alembic_config, 'head')
    
    # Then test downgrade for each revision
    for revision in reversed(get_revisions):
        downgrade(alembic_config, revision)
        if revision != get_revisions[0]:  # Don't check after downgrading first revision
            upgrade(alembic_config, revision)  # Upgrade again to test next downgrade

def test_performance_indexes_exist(alembic_engine: Engine):
    """Test that performance indexes are created correctly."""
    # Upgrade to the performance indexes migration
    upgrade(alembic_config, '002')
    
    inspector = inspect(alembic_engine)
    
    # Check document indexes
    doc_indexes = {idx['name']: idx for idx in inspector.get_indexes('document')}
    assert 'idx_document_processed_created' in doc_indexes
    assert 'idx_document_metadata_gin' in doc_indexes
    
    # Check semantic block indexes
    block_indexes = {idx['name']: idx for idx in inspector.get_indexes('semantic_block')}
    assert 'idx_semantic_block_created' in block_indexes
    assert 'idx_semantic_block_metadata_gin' in block_indexes
    assert 'idx_semantic_block_content_gist' in block_indexes
    
    # Check proposal indexes
    prop_indexes = {idx['name']: idx for idx in inspector.get_indexes('proposal')}
    assert 'idx_proposal_created_status' in prop_indexes
    assert 'idx_proposal_parameters_gin' in prop_indexes
    assert 'idx_proposal_content_gin' in prop_indexes

def test_seed_data_development(alembic_engine: Engine):
    """Test that development seed data is inserted correctly."""
    # Set environment to development
    import os
    os.environ['APP_ENV'] = 'development'
    
    # Upgrade to the seed data migration
    upgrade(alembic_config, '003')
    
    with alembic_engine.connect() as conn:
        # Check documents
        result = conn.execute(text("SELECT COUNT(*) FROM document")).scalar()
        assert result == 2  # Should have two documents in dev environment
        
        # Check semantic blocks
        result = conn.execute(text("SELECT COUNT(*) FROM semantic_block")).scalar()
        assert result == 2  # Should have two blocks
        
        # Check proposals
        result = conn.execute(text("SELECT COUNT(*) FROM proposal")).scalar()
        assert result == 1  # Should have one proposal
        
        # Verify specific data
        proposal = conn.execute(
            text("SELECT title, client_name, status FROM proposal LIMIT 1")
        ).fetchone()
        assert proposal.title == 'Enterprise Cloud Support'
        assert proposal.client_name == 'FinTech Corp'
        assert proposal.status == 'approved'

def test_seed_data_test_environment(alembic_engine: Engine):
    """Test that test environment seed data is inserted correctly."""
    # Set environment to test
    import os
    os.environ['APP_ENV'] = 'test'
    
    # Upgrade to the seed data migration
    upgrade(alembic_config, '003')
    
    with alembic_engine.connect() as conn:
        # Check documents
        result = conn.execute(text("SELECT COUNT(*) FROM document")).scalar()
        assert result == 1  # Should have one document in test environment
        
        # Check semantic blocks
        result = conn.execute(text("SELECT COUNT(*) FROM semantic_block")).scalar()
        assert result == 1  # Should have one block
        
        # Check proposals
        result = conn.execute(text("SELECT COUNT(*) FROM proposal")).scalar()
        assert result == 1  # Should have one proposal
