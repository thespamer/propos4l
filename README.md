# 🚀 Propos4l - Automação Inteligente de Propostas

Bem-vindo ao Propos4l, uma solução inovadora para automação e geração de propostas comerciais e técnicas para consultoria de TI. Este sistema utiliza Inteligência Artificial para transformar o processo manual de criação de propostas em um fluxo eficiente e inteligente.

## 📋 Visão Geral

O Propos4l resolve o desafio comum em empresas de consultoria de TI: a criação manual e repetitiva de propostas comerciais. Utilizando tecnologias modernas como LLMs (Large Language Models) e processamento de linguagem natural, o sistema aprende com propostas anteriores para gerar novos documentos personalizados e profissionais.

### 🔄 Fluxo de Trabalho

```mermaid
flowchart LR
    A[PDF Existente] -->|Upload| B[Processamento OCR]
    B --> C[Extração de Blocos]
    C --> D[Armazenamento Vetorial]
    E[Nova Requisição] -->|Parâmetros| F[Geração IA]
    D -->|Contexto| F
    F --> G[Proposta Final]
    G -->|Export| H[PDF/Word/HTML]
```

## 🏗️ Arquitetura do Sistema

### Visão Geral da Arquitetura

```mermaid
C4Context
  Enterprise_Boundary(b0, "Propos4l System") {
    Person(user, "Usuário", "Consultor de TI")
    
    System_Boundary(b1, "Propos4l Platform") {
      Container(web_app, "Frontend", "Next.js", "Interface do usuário")
      Container(api, "Backend API", "FastAPI", "Processamento e geração")
      ContainerDb(db, "Database", "PostgreSQL", "Dados persistentes")
      ContainerDb(vector_db, "Vector Store", "FAISS", "Busca semântica")
      Container(cache, "Cache", "Redis", "Cache e filas")
    }
    
    System_Ext(llm, "LLM Service", "Serviço de IA")
    System_Ext(storage, "Object Storage", "Armazenamento de PDFs")
  }
  
  Rel(user, web_app, "Usa", "HTTPS")
  Rel(web_app, api, "Chama", "REST")
  Rel(api, db, "Lê/Escreve")
  Rel(api, vector_db, "Consulta")
  Rel(api, cache, "Usa")
  Rel(api, llm, "Gera texto", "API")
  Rel(api, storage, "Armazena", "S3")
```

### Componentes do Frontend

```mermaid
flowchart TB
    subgraph Components["Componentes React"]
        direction TB
        App["App Root"] --> Layout["Layout"]
        Layout --> Nav["Navigation"]
        Layout --> Main["Main Content"]
        
        Main --> Upload["Upload Form"]
        Main --> Generator["Proposal Generator"]
        Main --> Preview["PDF Preview"]
        
        subgraph Contexts["Contextos Globais"]
            direction LR
            Toast["Toast Context"]
            Loading["Loading Context"]
            Auth["Auth Context"]
        end
        
        Upload --> Toast
        Generator --> Toast
        Upload --> Loading
        Generator --> Loading
        App --> Auth
    end
```

### Modelo de Dados

```mermaid
erDiagram
    PROPOSAL ||--o{ SECTION : contains
    PROPOSAL ||--o{ METADATA : has
    PROPOSAL ||--|| TEMPLATE : uses
    SECTION ||--o{ BLOCK : contains
    
    PROPOSAL {
        uuid id PK
        string title
        string client_name
        string industry
        timestamp created_at
        string status
    }
    
    SECTION {
        uuid id PK
        uuid proposal_id FK
        string name
        int order
        text content
    }
    
    BLOCK {
        uuid id PK
        uuid section_id FK
        string type
        text content
        json metadata
    }
    
    METADATA {
        uuid id PK
        uuid proposal_id FK
        string key
        string value
    }
    
    TEMPLATE {
        uuid id PK
        string name
        json structure
        boolean is_active
    }
```

```mermaid
flowchart TB
    subgraph Frontend["Frontend (Next.js)"]    
        UI["Interface do Usuário"] --> ApiClient["API Client"]
    end

    subgraph Backend["Backend (FastAPI)"]    
        API["API REST"] --> PG["Proposal Generator"]
        API --> PP["PDF Processor"]
        API --> VS["Vector Store"]
        
        PG -->|Gera| DB[(PostgreSQL)]
        PP -->|Armazena| DB
        VS -->|Consulta| VDB[(Vector DB)]
    end

    subgraph Services["Serviços Externos"]
        LLM["LLM (Ollama)"] 
        Redis["Cache (Redis)"]
    end

    ApiClient -->|HTTP| API
    PG -->|Prompt| LLM
    VS -->|Cache| Redis
```

## 💡 Funcionalidades Principais

### Arquitetura de Processamento

```mermaid
flowchart TB
    subgraph Input["Entrada de Dados"]
        PDF["PDF Upload"] --> OCR["OCR Engine"]
        Form["Form Input"] --> Validation["Validação"]
    end
    
    subgraph Processing["Processamento"]
        OCR --> TextExtraction["Extração de Texto"]
        TextExtraction --> Chunking["Chunking"]
        Chunking --> Embedding["Embedding"]
        
        Validation --> ParamProcess["Processamento de Parâmetros"]
        ParamProcess --> Context["Contexto"]
        
        Embedding --> VectorDB["Vector Database"]
        VectorDB --> SimilaritySearch["Busca por Similaridade"]
        SimilaritySearch --> Context
    end
    
    subgraph Generation["Geração"]
        Context --> PromptGen["Geração de Prompt"]
        PromptGen --> LLM["LLM"]
        LLM --> PostProcess["Pós-processamento"]
    end
    
    subgraph Output["Saída"]
        PostProcess --> Template["Template"]
        Template --> FinalDoc["Documento Final"]
        FinalDoc --> Export["Exportação"]        
    end
```

### 1. Processamento Inteligente de PDFs

```mermaid
sequenceDiagram
    participant U as Usuário
    participant API as Backend API
    participant OCR as OCR Engine
    participant LLM as Language Model
    participant DB as Vector Store

    U->>API: Upload PDF
    API->>OCR: Processar Documento
    OCR->>API: Texto Extraído
    API->>LLM: Identificar Seções
    LLM->>API: Blocos Categorizados
    API->>DB: Armazenar Vetores
    API->>U: Confirmação
```

- 📄 OCR para documentos digitalizados
- 🔍 Identificação automática de seções
- 📊 Categorização inteligente de conteúdo
- 🔤 Processamento de múltiplos formatos

### 2. Geração de Propostas

```mermaid
sequenceDiagram
    participant U as Usuário
    participant API as Backend API
    participant VS as Vector Store
    participant LLM as Language Model
    participant T as Templates

    U->>API: Requisitar Proposta
    API->>VS: Buscar Similares
    VS->>API: Contexto Relevante
    API->>LLM: Gerar Conteúdo
    API->>T: Aplicar Template
    API->>U: Proposta Final
```

- 🎯 Personalização por cliente/indústria
- 📝 Sugestões inteligentes
- 🔄 Múltiplos formatos de exportação
- 📊 Templates personalizáveis

## 🛠️ Stack Tecnológico

### Frontend
- **Next.js 14**: Framework React moderno
- **Tailwind CSS**: Estilização moderna
- **React Context**: Gerenciamento de estado

### Backend
- **FastAPI**: API REST assíncrona
- **LangChain**: Orquestração de LLMs
- **FAISS**: Busca vetorial eficiente
- **PostgreSQL**: Armazenamento persistente
- **Redis**: Cache e filas

## 🚀 Começando

### Pré-requisitos
- Docker e Docker Compose
- Chave de API para LLM (opcional)

### Instalação com Docker

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/propos4l.git
cd propos4l
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

3. Inicie os serviços:
```bash
docker compose up -d
```

### Endpoints da API

#### `GET /api/health`
- Status da API e métricas

#### `POST /api/proposals/upload`
- Upload e processamento de PDFs
```typescript
interface UploadRequest {
  file: File
  metadata: {
    clientName: string
    industry: string
    date: string
  }
}
```

#### `POST /api/proposals/generate`
- Geração de novas propostas
```typescript
interface GenerateRequest {
  clientName: string
  industry: string
  requirements: string
  scope?: string
  timeline?: string
  budget?: string
}
```

## 📈 Fluxo de Desenvolvimento

### Ciclo de Desenvolvimento

```mermaid
stateDiagram-v2
    [*] --> Development
    Development --> Testing: Commit
    Testing --> QA: Tests Pass
    QA --> Production: Approval
    Production --> [*]
    
    Testing --> Development: Fails
    QA --> Development: Changes Needed
```

### Pipeline de CI/CD

```mermaid
flowchart LR
    subgraph Local["Desenvolvimento Local"]
        Dev["Desenvolvimento"] --> Test["Testes Locais"]
    end
    
    subgraph CI["Integração Contínua"]
        Push["Git Push"] --> Lint["Linting"]
        Lint --> Build["Build"]
        Build --> UnitTest["Testes Unitários"]
        UnitTest --> IntegTest["Testes de Integração"]
    end
    
    
    subgraph CD["Entrega Contínua"]
        IntegTest --> Stage["Staging"]
        Stage --> E2E["Testes E2E"]
        E2E --> Prod["Produção"]
    end
    
    Test --> Push
    Prod --> Monitor["Monitoramento"]
```

### Fluxo de Dados em Tempo Real

```mermaid
sequenceDiagram
    participant U as Usuário
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    participant Cache as Redis
    
    U->>FE: Inicia geração
    FE->>BE: POST /generate
    BE->>Cache: Cria job
    Cache-->>FE: Job ID
    FE->>BE: GET /status/{jobId}
    BE->>Cache: Verifica status
    Cache-->>BE: Status atual
    BE-->>FE: Atualização
    FE-->>U: Feedback visual
    
    loop Cada 2s
        FE->>BE: GET /status/{jobId}
        BE->>Cache: Verifica status
        Cache-->>BE: Status atual
        BE-->>FE: Atualização
        FE-->>U: Progresso
    end
    
    BE->>DB: Salva resultado
    DB-->>BE: Confirmação
    BE-->>FE: Conclusão
    FE-->>U: Download disponível
```

```mermaid
stateDiagram-v2
    [*] --> Development
    Development --> Testing: Commit
    Testing --> QA: Tests Pass
    QA --> Production: Approval
    Production --> [*]
    
    Testing --> Development: Fails
    QA --> Development: Changes Needed
```

## 🚀 Iniciando o Projeto

### Pré-requisitos

- Docker e Docker Compose
- Git
- Node.js 18+ (para desenvolvimento frontend)
- Python 3.11+ (para desenvolvimento backend)

### Iniciando com Docker

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/propos4l.git
cd propos4l
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

3. Inicie os serviços:
```bash
docker compose up -d
```

4. Verifique o status dos serviços:
```bash
docker compose ps
```

5. Acesse a aplicação:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### Iniciando em Modo de Desenvolvimento

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Iniciando Migrations

```bash
docker compose run migrations alembic upgrade head
```

### Parando os Serviços

```bash
docker compose down
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Amazing Feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
