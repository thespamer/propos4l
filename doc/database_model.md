# Modelo de Banco de Dados do Propos4l

## Modelo Entidade-Relacionamento

```mermaid
erDiagram
    PROPOSALS ||--o{ SECTIONS : contains
    PROPOSALS ||--o{ METADATA : has
    PROPOSALS ||--|| TEMPLATES : uses
    SECTIONS ||--o{ BLOCKS : contains
    PROPOSALS ||--o{ COMMENTS : has
    PROPOSALS ||--o{ VERSIONS : tracks
    USERS ||--o{ PROPOSALS : creates
    USERS ||--o{ COMMENTS : makes
    
    PROPOSALS {
        uuid id PK
        string title
        string client_name
        string industry
        timestamp created_at
        string status
        uuid creator_id FK
        uuid template_id FK
        timestamp updated_at
        boolean is_archived
    }
    
    SECTIONS {
        uuid id PK
        uuid proposal_id FK
        string name
        int order
        text content
        timestamp created_at
        timestamp updated_at
    }
    
    BLOCKS {
        uuid id PK
        uuid section_id FK
        string type
        text content
        jsonb metadata
        timestamp created_at
        float confidence_score
    }
    
    METADATA {
        uuid id PK
        uuid proposal_id FK
        string key
        string value
        timestamp created_at
    }
    
    TEMPLATES {
        uuid id PK
        string name
        jsonb structure
        boolean is_active
        timestamp created_at
        timestamp updated_at
        string version
    }
    
    USERS {
        uuid id PK
        string email
        string name
        string hashed_password
        timestamp created_at
        boolean is_active
        jsonb preferences
    }
    
    COMMENTS {
        uuid id PK
        uuid proposal_id FK
        uuid user_id FK
        text content
        timestamp created_at
        uuid parent_id FK
        boolean is_resolved
    }
    
    VERSIONS {
        uuid id PK
        uuid proposal_id FK
        int version_number
        jsonb content
        timestamp created_at
        uuid creator_id FK
        string change_description
    }
```

## Índices e Constraints

```sql
-- Proposals
CREATE INDEX idx_proposals_client_name ON proposals(client_name);
CREATE INDEX idx_proposals_industry ON proposals(industry);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_created_at ON proposals(created_at);

-- Sections
CREATE INDEX idx_sections_proposal_id ON sections(proposal_id);
CREATE INDEX idx_sections_order ON sections(proposal_id, "order");

-- Blocks
CREATE INDEX idx_blocks_section_id ON blocks(section_id);
CREATE INDEX idx_blocks_type ON blocks(type);
CREATE INDEX idx_blocks_confidence ON blocks(confidence_score);

-- Templates
CREATE INDEX idx_templates_active ON templates(is_active);
CREATE INDEX idx_templates_name ON templates(name);

-- Comments
CREATE INDEX idx_comments_proposal_id ON comments(proposal_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);

-- Versions
CREATE INDEX idx_versions_proposal_id ON versions(proposal_id);
CREATE INDEX idx_versions_number ON versions(proposal_id, version_number);
```

## Modelo de Vetores FAISS

```mermaid
flowchart TB
    subgraph VectorDB["Vector Database (FAISS)"]
        direction TB
        Index["Índice Principal"]
        Metadata["Metadados"]
        
        subgraph Vectors["Vetores"]
            direction TB
            ProposalVecs["Vetores de Propostas"]
            BlockVecs["Vetores de Blocos"]
            TemplateVecs["Vetores de Templates"]
        end
        
        subgraph Mapping["Mapeamento"]
            direction LR
            VecToID["Vetor → ID"]
            IDToMetadata["ID → Metadados"]
        end
        
        %% Conexões
        Index -->|"indexa"| ProposalVecs
        Index -->|"indexa"| BlockVecs
        Index -->|"indexa"| TemplateVecs
        ProposalVecs -->|"mapeia"| VecToID
        BlockVecs -->|"mapeia"| VecToID
        TemplateVecs -->|"mapeia"| VecToID
        VecToID -->|"resolve"| IDToMetadata
        IDToMetadata -->|"consulta"| Metadata
    end
```

## Cache Redis

```mermaid
flowchart TB
    subgraph Redis["Redis Cache"]
        direction TB
        Jobs["Jobs Queue"]
        Sessions["Sessions"]
        ProposalCache["Proposal Cache"]
        
        subgraph JobStatus["Status dos Jobs"]
            direction LR
            Pending["Pendentes"]
            Processing["Em Processamento"]
            Completed["Concluídos"]
            
            Pending -->|"inicia"| Processing
            Processing -->|"finaliza"| Completed
        end
        
        subgraph CacheKeys["Chaves de Cache"]
            direction TB
            UserData["Dados do Usuário"]
            TemplateData["Templates"]
            ProposalData["Propostas"]
        end
        
        %% Conexões
        Jobs -->|"gerencia"| JobStatus
        Sessions -->|"armazena"| UserData
        ProposalCache -->|"utiliza"| CacheKeys
    end
```
