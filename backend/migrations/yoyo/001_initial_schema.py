"""
Initial schema
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        # Apply migration
        """
        -- Create tables with explicit VARCHAR types instead of ENUMs
        CREATE TABLE document (
            id SERIAL PRIMARY KEY,
            filename VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            file_hash VARCHAR NOT NULL,
            ocr_status VARCHAR NOT NULL DEFAULT 'pending',
            raw_text TEXT,
            language VARCHAR,
            document_metadata JSONB DEFAULT '{}'::jsonb,
            vector_id VARCHAR,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_document_created_at ON document (created_at);
        CREATE INDEX ix_document_filename ON document (filename);
        CREATE INDEX ix_document_file_hash ON document (file_hash);
        
        CREATE TABLE document_page (
            id SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL REFERENCES document(id) ON DELETE CASCADE,
            page_number INTEGER NOT NULL,
            page_text TEXT,
            page_image_path VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_document_page_document_id ON document_page (document_id);
        CREATE INDEX ix_document_page_created_at ON document_page (created_at);
        
        CREATE TABLE semantic_block (
            id SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL REFERENCES document(id) ON DELETE CASCADE,
            page_number INTEGER,
            text TEXT NOT NULL,
            embedding_id VARCHAR,
            block_type VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_semantic_block_document_id ON semantic_block (document_id);
        CREATE INDEX ix_semantic_block_block_type ON semantic_block (block_type);
        CREATE INDEX ix_semantic_block_created_at ON semantic_block (created_at);
        
        CREATE TABLE proposal (
            id SERIAL PRIMARY KEY,
            title VARCHAR NOT NULL,
            client_name VARCHAR,
            status VARCHAR NOT NULL DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_proposal_created_at ON proposal (created_at);
        
        CREATE TABLE proposal_block (
            id SERIAL PRIMARY KEY,
            proposal_id INTEGER NOT NULL REFERENCES proposal(id) ON DELETE CASCADE,
            block_type VARCHAR NOT NULL,
            content TEXT NOT NULL,
            "order" INTEGER NOT NULL,
            source_block_id INTEGER REFERENCES semantic_block(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_proposal_block_proposal_id ON proposal_block (proposal_id);
        CREATE INDEX ix_proposal_block_block_type ON proposal_block (block_type);
        CREATE INDEX ix_proposal_block_created_at ON proposal_block (created_at);
        
        CREATE TABLE document_proposal (
            id SERIAL PRIMARY KEY,
            document_id INTEGER NOT NULL REFERENCES document(id) ON DELETE CASCADE,
            proposal_id INTEGER NOT NULL REFERENCES proposal(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_document_proposal_document_id ON document_proposal (document_id);
        CREATE INDEX ix_document_proposal_proposal_id ON document_proposal (proposal_id);
        CREATE INDEX ix_document_proposal_created_at ON document_proposal (created_at);
        
        CREATE TABLE template (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            description TEXT,
            file_path VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_template_created_at ON template (created_at);
        
        CREATE TABLE proposal_template (
            id SERIAL PRIMARY KEY,
            proposal_id INTEGER NOT NULL REFERENCES proposal(id) ON DELETE CASCADE,
            template_id INTEGER NOT NULL REFERENCES template(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX ix_proposal_template_proposal_id ON proposal_template (proposal_id);
        CREATE INDEX ix_proposal_template_template_id ON proposal_template (template_id);
        CREATE INDEX ix_proposal_template_created_at ON proposal_template (created_at);
        
        CREATE TABLE comment (
            id SERIAL PRIMARY KEY,
            proposal_id INTEGER NOT NULL REFERENCES proposal(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            section VARCHAR,
            parent_id INTEGER REFERENCES comment(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
        
        CREATE INDEX ix_comment_proposal_id ON comment (proposal_id);
        """,
        
        # Rollback migration
        """
        DROP TABLE IF EXISTS proposal_template CASCADE;
        DROP TABLE IF EXISTS template CASCADE;
        DROP TABLE IF EXISTS document_proposal CASCADE;
        DROP TABLE IF EXISTS comment CASCADE;
        DROP TABLE IF EXISTS proposal_block CASCADE;
        DROP TABLE IF EXISTS proposal CASCADE;
        DROP TABLE IF EXISTS semantic_block CASCADE;
        DROP TABLE IF EXISTS document_page CASCADE;
        DROP TABLE IF EXISTS document CASCADE;
        """
    )
]
