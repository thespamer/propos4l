from datetime import datetime
from typing import Optional, List, Dict
from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional, Dict, Any
from sqlalchemy import JSON

# Constantes para tipos de blocos (em vez de usar Enum para evitar problemas com Alembic)
class BlockType:
    TITLE = "title"
    CLIENT = "client"
    CONTEXT = "context"
    PROBLEM = "problem"
    SOLUTION = "solution"
    SCOPE = "scope"
    TIMELINE = "timeline"
    INVESTMENT = "investment"
    DIFFERENTIALS = "differentials"
    CASES = "cases"
    OTHER = "other"
    
    @classmethod
    def values(cls) -> List[str]:
        """Retorna todos os valores possíveis"""
        return [value for key, value in cls.__dict__.items() 
                if not key.startswith('_') and isinstance(value, str)]

class DocumentProposalLink(SQLModel, table=True):
    """Many-to-many relationship between documents and proposals"""
    document_id: Optional[int] = Field(
        default=None, foreign_key="document.id", primary_key=True
    )
    proposal_id: Optional[int] = Field(
        default=None, foreign_key="proposal.id", primary_key=True
    )

class Document(SQLModel, table=True):
    """Represents a source document (PDF proposal)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_hash: str = Field(index=True)  # For deduplication
    ocr_status: str = Field(default="pending")  # pending, processing, completed, failed
    raw_text: str
    language: Optional[str] = None
    document_metadata: dict = Field(default_factory=dict, sa_type=JSON)
    vector_id: Optional[str] = None  # ID in the vector store
    
    # Relationships
    blocks: List["SemanticBlock"] = Relationship(back_populates="document")
    proposals: List["Proposal"] = Relationship(back_populates="source_documents", link_model=DocumentProposalLink)

class SemanticBlock(SQLModel, table=True):
    """Represents a semantic block extracted from a document"""
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    block_type: str  # Usar str em vez de BlockType para evitar criação de ENUM no banco
    content: str
    start_position: int  # Character position in document
    end_position: int
    confidence_score: float  # Confidence in block type classification
    language_patterns: dict = Field(default_factory=dict, sa_type=JSON)  # Identified patterns
    formatting_metadata: dict = Field(default_factory=dict, sa_type=JSON)  # Font, style, etc.
    vector_id: Optional[str] = None  # ID in the vector store
    
    # Relationships
    document: Document = Relationship(back_populates="blocks")
    used_in_proposals: List["ProposalBlock"] = Relationship(back_populates="source_block")

class Proposal(SQLModel, table=True):
    """Represents a generated proposal"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    client_name: str
    industry: str
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="draft")  # draft, review, approved, archived
    proposal_metadata: dict = Field(default_factory=dict, sa_type=JSON)
    vector_id: Optional[str] = None  # ID in the vector store
    current_version: int = Field(default=1)
    
    # Relationships
    blocks: List["ProposalBlock"] = Relationship(back_populates="proposal")
    source_documents: List[Document] = Relationship(back_populates="proposals", 
                                                  link_model=DocumentProposalLink)
    versions: List["ProposalVersion"] = Relationship(back_populates="proposal")
    comments: List["Comment"] = Relationship(back_populates="proposal")

class ProposalBlock(SQLModel, table=True):
    """Represents a block in a generated proposal"""
    id: Optional[int] = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id")
    block_type: str  # Usar str em vez de BlockType para evitar criação de ENUM no banco
    content: str
    order: int  # Position in the proposal
    is_ai_generated: bool = Field(default=False)
    source_block_id: Optional[int] = Field(foreign_key="semanticblock.id")
    generation_params: dict = Field(default_factory=dict, sa_type=JSON)  # AI generation parameters
    
    # Relationships
    proposal: Proposal = Relationship(back_populates="blocks")
    source_block: Optional[SemanticBlock] = Relationship(back_populates="used_in_proposals")

class User(SQLModel, table=True):
    """Represents a user in the system"""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(index=True)
    full_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    comments: List["Comment"] = Relationship(back_populates="user")
    proposal_versions: List["ProposalVersion"] = Relationship(back_populates="created_by_user")

class ProposalVersion(SQLModel, table=True):
    """Represents a version of a proposal"""
    id: Optional[int] = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id")
    version_number: int
    content: dict = Field(sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(foreign_key="user.id")
    version_notes: str = Field(default="")
    
    # Relationships
    proposal: Proposal = Relationship(back_populates="versions")
    created_by_user: User = Relationship(back_populates="proposal_versions")

class Comment(SQLModel, table=True):
    """Represents a comment on a proposal"""
    id: Optional[int] = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id")
    user_id: int = Field(foreign_key="user.id")
    content: str
    section: Optional[str] = None  # References the section being commented on
    parent_id: Optional[int] = Field(default=None, foreign_key="comment.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    proposal: Proposal = Relationship(back_populates="comments")
    user: User = Relationship(back_populates="comments")
    replies: List["Comment"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": [id],
            "cascade": "all, delete-orphan"
        }
    )

class Template(SQLModel, table=True):
    """Represents a proposal template that can be used to generate new proposals"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = Field(default="")
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    source_document_id: Optional[int] = Field(foreign_key="document.id")
    structure: Dict = Field(default_factory=dict, sa_type=JSON)  # Structure of the template
    
    # Relationships
    sections: List["TemplateSection"] = Relationship(back_populates="template")
    source_document: Optional[Document] = Relationship()

class TemplateSection(SQLModel, table=True):
    """Represents a section in a proposal template"""
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="template.id")
    name: str  # Maps to BlockType
    content: str  # Default content or placeholder
    order: int  # Position in the template
    section_metadata: Dict = Field(default_factory=dict, sa_type=JSON)  # Additional metadata
    
    # Relationships
    template: Template = Relationship(back_populates="sections")
