# 🚀 Propos4l - Automação Inteligente de Propostas

## 💼 Transformando o Processo Comercial com IA de Ponta

O **Propos4l** revoluciona a maneira como consultorias de TI criam e gerenciam propostas comerciais, reduzindo de **dias para minutos** o tempo necessário para elaborar documentos profissionais e personalizados. Nossa plataforma combina o poder de **Large Language Models (LLMs)**, **Processamento de Linguagem Natural (NLP)** e **Busca Vetorial de Alta Precisão** para transformar sua base de conhecimento em uma poderosa ferramenta de geração de propostas.

### 🔥 Diferenciais de Negócio

- **Aumento de 300% na Produtividade da Equipe Comercial**: Automatize tarefas repetitivas e foque no que realmente importa - relacionamento com clientes e fechamento de negócios
- **Consistência e Qualidade Garantidas**: Templates inteligentes extraídos de suas melhores propostas garantem consistência na comunicação da marca
- **Redução de 70% no Ciclo de Vendas**: Responda a RFPs e oportunidades com rapidez inigualável, superando a concorrência
- **Análise Preditiva de Sucesso**: Algoritmos avançados identificam padrões em propostas vencedoras para maximizar taxas de conversão
- **Escalabilidade Imediata**: Capacite novos vendedores com o conhecimento institucional da empresa desde o primeiro dia

Bem-vindo ao Propos4l, uma solução inovadora para automação e geração de propostas comerciais e técnicas para consultoria de TI. Este sistema utiliza Inteligência Artificial para transformar o processo manual de criação de propostas em um fluxo eficiente e inteligente.

## 📋 Visão Geral

O Propos4l resolve o desafio comum em empresas de consultoria de TI: a criação manual e repetitiva de propostas comerciais. Utilizando tecnologias modernas como LLMs (Large Language Models) e processamento de linguagem natural, o sistema aprende com propostas anteriores para gerar novos documentos personalizados e profissionais.

### 🔄 Fluxo de Trabalho

```mermaid
flowchart LR
    A["PDF Existente"]
    B["Processamento OCR"]
    C["Extração de Blocos"]
    D["Armazenamento Vetorial"]
    E["Nova Requisição"]
    F["Geração IA"]
    G["Proposta Final"]
    H["PDF/Word/HTML"]
    
    A -->|"Upload"| B
    B --> C
    C --> D
    E -->|"Parâmetros"| F
    D -->|"Contexto"| F
    F --> G
    G -->|"Export"| H
```

### 🔍 Processamento Inteligente de Documentos

O Propos4l utiliza um pipeline sofisticado de processamento de documentos que combina várias tecnologias de ponta:

#### 1. Extração de Texto
- Processamento direto de PDFs usando PyMuPDF
- OCR (Reconhecimento Óptico de Caracteres) para páginas digitalizadas
- Preservação de metadados de formatação (fontes, estilos, layouts)

#### 2. Análise Inteligente
- **Entidades**: Identificação de pessoas, empresas, locais e datas
- **Termos Técnicos**: Reconhecimento de termos específicos da área de TI
- **Palavras-Chave**: Extração das frases mais relevantes do documento
- **Complexidade**: Análise da estrutura e complexidade do texto

#### 3. Identificação de Seções
- Detecção automática de seções comuns em propostas:
  - Título e informações do projeto
  - Contexto e situação atual
  - Problema e necessidades do cliente
  - Solução proposta
  - Escopo e entregas
  - Cronograma
  - Investimento e custos
  - Diferenciais competitivos

#### 4. Otimizações de Performance
- Processamento em lotes para maior eficiência
- Cache inteligente para operações frequentes
- Processamento paralelo de tarefas
- Vetorização para busca semântica rápida

#### 5. Monitoramento em Tempo Real
- Interface visual com progresso detalhado
- Barra de progresso animada
- Tempo estimado de conclusão
- Status de cada etapa do processamento
- Indicadores de sucesso/erro
- Métricas de performance

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
        App["App Root"]
        Layout["Layout"]
        Nav["Navigation"]
        Main["Main Content"]
        Upload["Upload Form"]
        Generator["Proposal Generator"]
        Preview["PDF Preview"]
        
        subgraph Contexts["Contextos Globais"]
            direction LR
            Toast["Toast Context"]
            Loading["Loading Context"]
            Auth["Auth Context"]
        end
        
        App --> Layout
        Layout --> Nav
        Layout --> Main
        Main --> Upload
        Main --> Generator
        Main --> Preview
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
        UI["Interface do Usuário"]
        ApiClient["API Client"]
        UI --> ApiClient
    end

    subgraph Backend["Backend (FastAPI)"]
        API["API REST"]
        PG["Proposal Generator"]
        PP["PDF Processor"]
        VS["Vector Store"]
        DB[("PostgreSQL")]
        VDB[("Vector DB")]
        
        API --> PG
        API --> PP
        API --> VS
        PG -->|Gera| DB
        PP -->|Armazena| DB
        VS -->|Consulta| VDB
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
        PDF["PDF Upload"]
        OCR["OCR Engine"]
        Form["Form Input"]
        Validation["Validação"]
        
        PDF --> OCR
        Form --> Validation
    end
    
    subgraph Processing["Processamento"]
        TextExtraction["Extração de Texto"]
        Chunking["Chunking"]
        Embedding["Embedding"]
        ParamProcess["Processamento de Parâmetros"]
        Context["Contexto"]
        VectorDB["Vector Database"]
        SimilaritySearch["Busca por Similaridade"]
        
        OCR --> TextExtraction
        TextExtraction --> Chunking
        Chunking --> Embedding
        Validation --> ParamProcess
        ParamProcess --> Context
        Embedding --> VectorDB
        VectorDB --> SimilaritySearch
        SimilaritySearch --> Context
    end
    
    subgraph Generation["Geração"]
        PromptGen["Geração de Prompt"]
        LLM["LLM"]
        PostProcess["Pós-processamento"]
        
        Context --> PromptGen
        PromptGen --> LLM
        LLM --> PostProcess
    end
    
    subgraph Output["Saída"]
        Template["Template"]
        FinalDoc["Documento Final"]
        Export["Exportação"]
        
        PostProcess --> Template
        Template --> FinalDoc
        FinalDoc --> Export
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

#### `POST /api/templates/`
- Geração de templates a partir de PDFs de propostas
```typescript
interface TemplateCreateRequest {
  file: File
  name: string
  description?: string
}
```

#### `GET /api/templates/`
- Listagem de templates disponíveis

#### `GET /api/templates/{template_id}`
- Detalhes de um template específico

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
        Dev["Desenvolvimento"]
        Test["Testes Locais"]
        Dev --> Test
    end
    
    subgraph CI["Integração Contínua"]
        Push["Git Push"]
        Lint["Linting"]
        Build["Build"]
        UnitTest["Testes Unitários"]
        IntegTest["Testes de Integração"]
        
        Push --> Lint
        Lint --> Build
        Build --> UnitTest
        UnitTest --> IntegTest
    end
    
    subgraph CD["Entrega Contínua"]
        Stage["Staging"]
        E2E["Testes E2E"]
        Prod["Produção"]
        Monitor["Monitoramento"]
        
        IntegTest --> Stage
        Stage --> E2E
        E2E --> Prod
        Prod --> Monitor
    end
    
    Test --> Push
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
