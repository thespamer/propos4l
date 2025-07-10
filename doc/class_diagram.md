# Diagramas de Classes do Propos4l

## Modelo de Classes Principal

```mermaid
classDiagram
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
        +create()
        +update()
        +delete()
        +export(format: ExportFormat)
    }

    class Section {
        +UUID id
        +UUID proposalId
        +String name
        +Integer order
        +String content
        +List~Block~ blocks
        +reorder(newOrder: Integer)
        +updateContent(content: String)
    }

    class Block {
        +UUID id
        +UUID sectionId
        +BlockType type
        +String content
        +JSON metadata
        +analyze()
        +validate()
    }

    class Template {
        +UUID id
        +String name
        +JSON structure
        +Boolean isActive
        +apply(proposal: Proposal)
        +validate()
    }

    class ProposalGenerator {
        -VectorStore vectorStore
        -LLMService llmService
        -TemplateEngine templateEngine
        +generateProposal(params: GenerationParams)
        +updateProposal(proposal: Proposal)
        -findSimilarProposals()
        -generateContent()
    }

    class PDFProcessor {
        -OCREngine ocrEngine
        -NLPService nlpService
        -VectorStore vectorStore
        +processDocument(file: File)
        +extractText()
        +identifySections()
        -vectorize()
    }

    class VectorStore {
        -FAISSIndex index
        -Database db
        +search(query: String, limit: Integer)
        +add(document: Document)
        +delete(id: UUID)
        -updateIndex()
    }

    Proposal "1" *-- "many" Section
    Section "1" *-- "many" Block
    Proposal "many" -- "1" Template
    ProposalGenerator -- VectorStore
    PDFProcessor -- VectorStore
```

## Diagrama de Classes do Frontend

```mermaid
classDiagram
    class App {
        +render()
    }

    class ProposalForm {
        -FormData formData
        -Boolean loading
        +handleSubmit()
        +handleInputChange()
        +validate()
    }

    class PDFUploader {
        -File file
        -UploadStatus status
        +handleUpload()
        +validateFile()
        -processUpload()
    }

    class PDFViewer {
        -String url
        -Number currentPage
        +nextPage()
        +previousPage()
        +zoom()
    }

    class ProposalList {
        -Array~Proposal~ proposals
        -Pagination pagination
        +loadProposals()
        +filterProposals()
        +sortProposals()
    }

    class ToastContext {
        -Array~Toast~ toasts
        +showToast()
        +hideToast()
    }

    class LoadingContext {
        -Boolean isLoading
        -String message
        +setLoading()
        +clearLoading()
    }

    App -- ProposalForm
    App -- PDFUploader
    App -- PDFViewer
    App -- ProposalList
    ProposalForm -- ToastContext
    PDFUploader -- LoadingContext
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
