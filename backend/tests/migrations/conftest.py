"""Migration test configuration and fixtures."""
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import os
from typing import Generator, List

def get_test_db_url() -> str:
    """Get test database URL."""
    return os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/propos4l_test'
    )

@pytest.fixture(scope='session')
def alembic_config() -> Config:
    """Create Alembic configuration."""
    config = Config()
    config.set_main_option('script_location', 'migrations')
    config.set_main_option('sqlalchemy.url', get_test_db_url())
    return config

@pytest.fixture(scope='session')
def alembic_engine() -> Generator[Engine, None, None]:
    """Create database engine for testing."""
    engine = create_engine(get_test_db_url())
    yield engine
    engine.dispose()

@pytest.fixture(scope='session')
def migration_context(alembic_engine: Engine) -> MigrationContext:
    """Create migration context."""
    with alembic_engine.connect() as connection:
        return MigrationContext.configure(connection)

@pytest.fixture(scope='session')
def get_revisions(alembic_config: Config) -> List[str]:
    """Get all migration revision IDs."""
    script = ScriptDirectory.from_config(alembic_config)
    revisions = []
    for revision in script.walk_revisions():
        revisions.append(revision.revision)
    return list(reversed(revisions))
