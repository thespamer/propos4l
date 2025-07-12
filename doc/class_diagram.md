# Diagramas de Classes do Propos4l

## Modelo de Classes Principal

```mermaid
classDiagram
    direction TB

    class Proposal {
        +UUID id
        +String title
        +String clientName
        +String industry
        +DateTime createdAt
        +ProposalStatus status
        +List~Section~ sections
        +Map~String,String~ metadata
        +Template template
        +create() void
        +update() void
        +delete() void
        +export(ExportFormat format) Document
    }

    class Section {
        +UUID id
        +UUID proposalId
        +String name
        +Integer order
        +String content
        +List~Block~ blocks
        +reorder(Integer newOrder) void
        +updateContent(String content) void
    }

    class Block {
        +UUID id
        +UUID sectionId
        +BlockType type
        +String content
        +JSON metadata
        +analyze() Analysis
        +validate() boolean
    }

    class Template {
        +UUID id
        +String name
        +JSON structure
        +Boolean isActive
        +apply(Proposal proposal) Document
        +validate() boolean
    }

    class ProposalGenerator {
        -VectorStore vectorStore
        -LLMService llmService
        -TemplateEngine templateEngine
        +generateProposal(GenerationParams params) Proposal
        +updateProposal(Proposal proposal) Proposal
        -findSimilarProposals() List~Proposal~
        -generateContent() String
    }

    class PDFProcessor {
        -OCREngine ocrEngine
        -NLPService nlpService
        -VectorStore vectorStore
        +processDocument(File file) Document
        +extractText() String
        +identifySections() List~Section~
        -vectorize() Vector
    }

    class VectorStore {
        -FAISSIndex index
        -Database db
        +search(String query, Integer limit) List~Document~
        +add(Document document) void
        +delete(UUID id) void
        -updateIndex() void
    }

    %% Relationships
    Proposal "1" *-- "many" Section : contains
    Section "1" *-- "many" Block : contains
    Proposal "many" -- "1" Template : uses
    ProposalGenerator ..> VectorStore : uses
    PDFProcessor ..> VectorStore : uses
```

## Diagrama de Classes do Frontend

```mermaid
classDiagram
    direction TB

    class App {
        +render() ReactNode
    }

    class ProposalForm {
        -FormData formData
        -Boolean loading
        +handleSubmit() Promise~void~
        +handleInputChange(Event e) void
        +validate() boolean
    }

    class PDFUploader {
        -File file
        -UploadStatus status
        +handleUpload() Promise~void~
        +validateFile() boolean
        -processUpload() Promise~void~
    }

    class PDFViewer {
        -String url
        -Number currentPage
        +nextPage() void
        +previousPage() void
        +zoom(Number scale) void
    }

    class ProposalList {
        -Array~Proposal~ proposals
        -Pagination pagination
        +loadProposals() Promise~void~
        +filterProposals(Filter filter) void
        +sortProposals(SortOption sort) void
    }

    class ToastContext {
        -Array~Toast~ toasts
        +showToast(ToastOptions options) void
        +hideToast(String id) void
    }

    class LoadingContext {
        -Boolean isLoading
        -String message
        +setLoading(String message) void
        +clearLoading() void
    }

    %% Relationships
    App ..> ProposalForm : renders
    App ..> PDFUploader : renders
    App ..> PDFViewer : renders
    App ..> ProposalList : renders
    ProposalForm ..> ToastContext : uses
    PDFUploader ..> LoadingContext : uses
```

## Diagrama de Classes de Serviços

```mermaid
classDiagram
    class APIService {
        -String baseUrl
        -Headers headers
        +get(endpoint: String)
        +post(endpoint: String, data: Any)
        +put(endpoint: String, data: Any)
        +delete(endpoint: String)
    }

    class ProposalService {
        -APIService api
        +createProposal(data: ProposalData)
        +updateProposal(id: UUID, data: ProposalData)
        +deleteProposal(id: UUID)
        +listProposals(filters: Filters)
    }

    class DocumentService {
        -APIService api
        -StorageService storage
        +uploadDocument(file: File)
        +processDocument(id: UUID)
        +downloadDocument(id: UUID)
    }

    class AuthService {
        -APIService api
        -TokenStorage storage
        +login(credentials: Credentials)
        +logout()
        +refreshToken()
        +isAuthenticated()
    }

    class StorageService {
        -S3Client client
        +uploadFile(file: File)
        +downloadFile(key: String)
        +deleteFile(key: String)
    }

    class CacheService {
        -RedisClient client
        +get(key: String)
        +set(key: String, value: Any)
        +delete(key: String)
        +expire(key: String, seconds: Number)
    }

    ProposalService -- APIService
    DocumentService -- APIService
    DocumentService -- StorageService
    AuthService -- APIService
