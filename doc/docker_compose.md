# Arquitetura Docker do Propos4l

## Dependências dos Serviços Docker

```mermaid
flowchart TB
    subgraph Services["Serviços Docker"]
        direction TB
        Frontend["frontend<br/>next:14"]
        Backend["backend<br/>python:3.11"]
        DB["postgres<br/>15.3-alpine"]
        Redis["redis<br/>7-alpine"]
        Ollama["ollama<br/>latest"]
        
        subgraph Volumes["Volumes"]
            direction LR
            PDFStorage["pdf_storage"]
            DBData["postgres_data"]
            Templates["templates"]
        end
        
        subgraph Networks["Networks"]
            direction LR
            AppNet["app_network"]
            DBNet["db_network"]
        end
        
        %% Service Dependencies
        Frontend -->|"depends_on"| Backend
        Backend -->|"depends_on"| DB
        Backend -->|"depends_on"| Redis
        Backend -->|"depends_on"| Ollama
        
        %% Volume Mounts
        Backend -.-|"mounts"| PDFStorage
        Backend -.-|"mounts"| Templates
        DB -.-|"mounts"| DBData
        
        %% Network Connections
        Frontend ---> AppNet
        Backend ---> AppNet
        Backend ---> DBNet
        DB ---> DBNet
        Redis ---> AppNet
        Ollama ---> AppNet
    end
```

## Configuração dos Serviços

```mermaid
flowchart TB
    subgraph Frontend["Frontend Service"]
        direction TB
        NextJS["Next.js App"]
        NodeModules["node_modules"]
        NextConfig["next.config.js"]
        
        subgraph FrontendEnv["Environment"]
            direction LR
            NEXT_PUBLIC_API_URL["API_URL"]
            NODE_ENV["NODE_ENV"]
        end
        
        NextJS --> NodeModules
        NextJS --> NextConfig
    end
    
    subgraph Backend["Backend Service"]
        direction TB
        FastAPI["FastAPI App"]
        PythonDeps["Python deps"]
        WeasyPrint["WeasyPrint"]
        
        subgraph BackendEnv["Environment"]
            direction LR
            DATABASE_URL["DATABASE_URL"]
            REDIS_URL["REDIS_URL"]
            OLLAMA_URL["OLLAMA_URL"]
        end
        
        FastAPI --> PythonDeps
        FastAPI --> WeasyPrint
    end
    
    subgraph Database["Database Service"]
        direction TB
        Postgres["PostgreSQL"]
        
        subgraph DBEnv["Environment"]
            direction LR
            POSTGRES_DB["POSTGRES_DB"]
            POSTGRES_USER["POSTGRES_USER"]
            POSTGRES_PASSWORD["POSTGRES_PASSWORD"]
        end
        
        Postgres --> DBEnv
    end
```

## Fluxo de Build e Deploy

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as Git Repo
    participant Docker as Docker Build
    participant Compose as Docker Compose
    
    Dev->>Git: Push Changes
    Git->>Docker: Trigger Build
    
    par Frontend Build
        Docker->>Docker: Build frontend image
        Docker->>Docker: Install dependencies
        Docker->>Docker: Build Next.js app
    and Backend Build
        Docker->>Docker: Build backend image
        Docker->>Docker: Install system deps
        Docker->>Docker: Install Python deps
    end
    
    Docker->>Compose: Images Ready
    Compose->>Compose: Start Services
    
    par Service Start
        Compose->>Compose: Start Database
        Compose->>Compose: Run Migrations
        Compose->>Compose: Start Redis
        Compose->>Compose: Start Ollama
        Compose->>Compose: Start Backend
        Compose->>Compose: Start Frontend
    end
```

## Volumes e Persistência

```mermaid
flowchart TB
    subgraph DockerVolumes["Docker Volumes"]
        direction TB
        subgraph Storage["Storage"]
            direction LR
            PDFStorage["pdf_storage<br/>Propostas PDF"]
            DBData["postgres_data<br/>Dados do Banco"]
            Templates["templates<br/>Templates HTML"]
        end
        
        subgraph Backup["Backup Strategy"]
            direction LR
            PDFBackup["PDF Backup<br/>Diário"]
            DBBackup["DB Backup<br/>A cada 6h"]
            TemplateBackup["Template Backup<br/>Por mudança"]
        end
        
        %% Backup Flows
        PDFStorage -->|"backup diário"| PDFBackup
        DBData -->|"backup 6h"| DBBackup
        Templates -->|"backup on change"| TemplateBackup
    end
```

## Monitoramento e Logs

```mermaid
flowchart TB
    subgraph Monitoring["Sistema de Monitoramento"]
        direction TB
        Logs["Container Logs"]
        Metrics["Métricas"]
        Traces["Traces"]
        
        subgraph LogAggregation["Agregação de Logs"]
            direction LR
            AppLogs["App Logs"]
            AccessLogs["Access Logs"]
            ErrorLogs["Error Logs"]
        end
        
        %% Log Flow
        Logs -->|"aplicação"| AppLogs
        Logs -->|"acesso"| AccessLogs
        Logs -->|"erro"| ErrorLogs
        
        %% Monitoring Flow
        AppLogs --> Metrics
        AccessLogs --> Metrics
        ErrorLogs --> Metrics
        Metrics --> Traces
    end
    
    Logs -->|collect| LogAggregation
    Metrics -->|collect| MetricsCollection
    
    AppLogs -->|alert| ErrorLogs
    CPU -->|threshold| Alerts["Alertas"]
    Memory -->|threshold| Alerts
    Disk -->|threshold| Alerts
```
