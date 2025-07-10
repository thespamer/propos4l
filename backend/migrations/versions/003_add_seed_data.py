"""Add seed data

Revision ID: 003
Revises: 002
Create Date: 2025-07-08 22:05:02.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime, timedelta
import json
import os

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

# Sample data for development environment
dev_documents = [
    {
        'filename': 'cloud_infrastructure_proposal.pdf',
        'file_path': '/storage/pdfs/cloud_infrastructure_proposal.pdf',
        'processed': True,
        'metadata': {
            'pages': 15,
            'language': 'en',
            'confidence': 0.95
        }
    },
    {
        'filename': 'data_analytics_proposal.pdf',
        'file_path': '/storage/pdfs/data_analytics_proposal.pdf',
        'processed': True,
        'metadata': {
            'pages': 12,
            'language': 'en',
            'confidence': 0.92
        }
    }
]

dev_blocks = [
    {
        'document_id': 1,
        'block_type': 'title',
        'content': 'Cloud Infrastructure Support Proposal',
        'page_number': 1,
        'position': {'x': 100, 'y': 100, 'width': 400, 'height': 50},
        'metadata': {
            'confidence': 0.98,
            'nlp_analysis': {
                'entities': {'SERVICE': ['Cloud Infrastructure']},
                'key_phrases': ['cloud', 'infrastructure', 'support'],
                'technical_terms': ['cloud infrastructure'],
                'text_structure': {'complexity_score': 0.3}
            }
        }
    },
    {
        'document_id': 1,
        'block_type': 'scope',
        'content': '24/7 cloud infrastructure support with 99.9% SLA',
        'page_number': 3,
        'position': {'x': 100, 'y': 300, 'width': 400, 'height': 100},
        'metadata': {
            'confidence': 0.95,
            'nlp_analysis': {
                'entities': {'SERVICE': ['cloud infrastructure'], 'METRIC': ['99.9%']},
                'key_phrases': ['24/7 support', 'SLA'],
                'technical_terms': ['SLA', 'infrastructure'],
                'text_structure': {'complexity_score': 0.5}
            }
        }
    }
]

dev_proposals = [
    {
        'title': 'Enterprise Cloud Support',
        'client_name': 'FinTech Corp',
        'status': 'approved',
        'parameters': {
            'service_type': 'cloud_support',
            'duration_months': 6,
            'team_size': 8,
            'sla_percentage': 99.9
        },
        'content': {
            'sections': {
                'overview': 'Enterprise-grade 24/7 cloud infrastructure support...',
                'solution': 'Hybrid team structure with dedicated support...',
                'timeline': '6-month implementation plan...',
                'investment': 'Monthly retainer model...'
            }
        },
        'metadata': {
            'generated_from': [1],
            'similarity_score': 0.85
        }
    }
]

def _insert_seed_data(is_test: bool = False):
    """Insert seed data based on environment"""
    conn = op.get_bind()
    
    # Insert documents
    documents = dev_documents
    if is_test:
        # Modify data for test environment if needed
        documents = dev_documents[:1]  # Use only first document for tests
    
    for doc in documents:
        conn.execute(
            sa.text(
                """
                INSERT INTO document (filename, file_path, processed, metadata)
                VALUES (:filename, :file_path, :processed, :metadata)
                """
            ),
            {
                'filename': doc['filename'],
                'file_path': doc['file_path'],
                'processed': doc['processed'],
                'metadata': json.dumps(doc['metadata'])
            }
        )
    
    # Insert semantic blocks
    blocks = dev_blocks
    if is_test:
        blocks = dev_blocks[:1]  # Use only first block for tests
    
    for block in blocks:
        conn.execute(
            sa.text(
                """
                INSERT INTO semantic_block (document_id, block_type, content, page_number, position, metadata)
                VALUES (:document_id, :block_type, :content, :page_number, :position, :metadata)
                """
            ),
            {
                'document_id': block['document_id'],
                'block_type': block['block_type'],
                'content': block['content'],
                'page_number': block['page_number'],
                'position': json.dumps(block['position']),
                'metadata': json.dumps(block['metadata'])
            }
        )
    
    # Insert proposals
    proposals = dev_proposals
    if is_test:
        proposals = dev_proposals[:1]  # Use only first proposal for tests
    
    for prop in proposals:
        conn.execute(
            sa.text(
                """
                INSERT INTO proposal (title, client_name, status, parameters, content, metadata)
                VALUES (:title, :client_name, :status, :parameters, :content, :metadata)
                """
            ),
            {
                'title': prop['title'],
                'client_name': prop['client_name'],
                'status': prop['status'],
                'parameters': json.dumps(prop['parameters']),
                'content': json.dumps(prop['content']),
                'metadata': json.dumps(prop['metadata'])
            }
        )

def upgrade() -> None:
    # Check environment
    env = os.getenv('APP_ENV', 'development')
    
    if env in ['development', 'test']:
        _insert_seed_data(is_test=(env == 'test'))

def downgrade() -> None:
    # Check environment
    env = os.getenv('APP_ENV', 'development')
    
    if env in ['development', 'test']:
        conn = op.get_bind()
        # Clear seed data
        conn.execute(sa.text("DELETE FROM proposal WHERE client_name = 'FinTech Corp'"))
        conn.execute(sa.text("DELETE FROM semantic_block WHERE document_id IN (SELECT id FROM document WHERE filename = 'cloud_infrastructure_proposal.pdf')"))
        conn.execute(sa.text("DELETE FROM document WHERE filename IN ('cloud_infrastructure_proposal.pdf', 'data_analytics_proposal.pdf')"))
