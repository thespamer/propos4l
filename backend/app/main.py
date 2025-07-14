from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from sqlmodel import Session
import os
import json
import hashlib

from app.api.endpoints.processing_status import router as processing_status_router
from app.api.endpoints.processing_history import router as processing_history_router
from app.api.endpoints.templates import router as templates_router

from app.services.proposal_generator import ProposalGenerator
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStore
from app.database import get_session
from app.models.database import Document, SemanticBlock, BlockType

app = FastAPI(title="Propos4l API", description="API for intelligent proposal automation")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(processing_status_router, prefix="/api", tags=["processing-status"])
app.include_router(processing_history_router, prefix="/api", tags=["processing-history"])
app.include_router(templates_router, prefix="/api/templates", tags=["templates"])

# Initialize services
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
proposals_dir = data_dir / "proposals"
proposals_dir.mkdir(exist_ok=True)

vector_store = VectorStore(index_path=str(data_dir / "proposals.index"))
proposal_generator = ProposalGenerator(vector_store=vector_store)
pdf_processor = PDFProcessor()

def save_proposal_metadata(proposal_id: str, metadata: dict):
    metadata_file = proposals_dir / f"{proposal_id}.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f)

def load_proposal_metadata(proposal_id: str) -> Optional[dict]:
    metadata_file = proposals_dir / f"{proposal_id}.json"
    if not metadata_file.exists():
        return None
    with open(metadata_file) as f:
        return json.load(f)

def list_proposal_metadata(page: int = 1, page_size: int = 10) -> List[dict]:
    metadata_files = sorted(proposals_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    proposals = []
    for file in metadata_files[start_idx:end_idx]:
        with open(file) as f:
            metadata = json.load(f)
            proposals.append(metadata)
    return proposals

@app.get("/")
async def root():
    doc_count = vector_store.get_total_documents()
    return {
        "message": "Propos4l API is running",
        "stored_proposals": doc_count
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

class ProposalMetadata(BaseModel):
    client_name: str
    industry: str
    date: str = Field(default_factory=lambda: datetime.now().isoformat())

class ProposalSummary(BaseModel):
    id: str
    client_name: str
    industry: str
    date: str
    status: str
    filename: Optional[str] = None

class ProposalDetail(BaseModel):
    id: str
    client_name: str
    industry: str
    date: str
    status: str
    content: Dict[str, str]
    sections: Dict[str, str]
    filename: Optional[str] = None
    similar_proposals: Optional[List[str]] = None

class SearchQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, str]] = None
    page: int = 1
    page_size: int = 10

@app.post("/upload-proposal", response_model=ProposalDetail)
async def upload_proposal(
    file: UploadFile = File(...),
    metadata: ProposalMetadata = None,
    session: Session = Depends(get_session)
):
    """
    Upload and process a single PDF proposal
    """
    try:
        contents = await file.read()
        
        # Process PDF and extract text with metadata
        document = await pdf_processor.process_pdf(
            pdf_content=contents,
            session=session
        )
        
        # Set filename after document is created
        document.filename = file.filename
        session.commit()
        
        # Identify and extract sections
        semantic_blocks = await pdf_processor.identify_sections(
            document=document,
            session=session
        )
        
        # Organize sections by type
        sections = {}
        for block in semantic_blocks:
            if block.confidence_score >= 0.7:  # Only include high-confidence blocks
                sections[block.block_type.value] = {
                    "content": block.content,
                    "confidence": block.confidence_score,
                    "language_patterns": block.language_patterns,
                    "formatting": block.formatting_metadata
                }
        
        # Generate unique ID
        proposal_id = f"proposal_{metadata.client_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add to vector store
        await vector_store.add_document(
            text=document.raw_text,
            metadata={
                "id": proposal_id,
                "filename": file.filename,
                "client_name": metadata.client_name if metadata else "",
                "industry": metadata.industry if metadata else "",
                "date": metadata.date if metadata else "",
                "ocr_status": document.ocr_status,
                "language_patterns": document.metadata.get("language_patterns", {}),
                "page_count": document.metadata.get("page_count", 0),
                "creation_date": document.metadata.get("creation_date"),
                "author": document.metadata.get("author"),
                "title": document.metadata.get("title")
            }
        )
        
        # Prepare proposal data
        proposal_data = {
            "id": proposal_id,
            "filename": file.filename,
            "client_name": metadata.client_name if metadata else "",
            "industry": metadata.industry if metadata else "",
            "date": metadata.date if metadata else datetime.now().isoformat(),
            "status": "processed",
            "content": {
                "raw_text": document.raw_text,
                "ocr_status": document.ocr_status
            },
            "sections": sections,
            "metadata": {
                "language_patterns": document.metadata.get("language_patterns", {}),
                "page_count": document.metadata.get("page_count", 0),
                "creation_date": document.metadata.get("creation_date"),
                "author": document.metadata.get("author"),
                "title": document.metadata.get("title")
            }
        }
        proposal_data = {
            "id": proposal_id,
            "client_name": metadata.client_name if metadata else "",
            "industry": metadata.industry if metadata else "",
            "date": metadata.date if metadata else datetime.now().isoformat(),
            "status": "uploaded",
            "content": {"full_text": content["full_text"]},
            "sections": sections,
            "filename": file.filename
        }
        save_proposal_metadata(proposal_id, proposal_data)
        
        return proposal_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProposalRequest(BaseModel):
    client_name: str
    industry: str
    requirements: str
    scope: Optional[str] = ""
    timeline: Optional[str] = ""
    budget: Optional[str] = ""

@app.post("/generate-proposal", response_model=ProposalDetail)
async def generate_proposal(params: ProposalRequest):
    """
    Generate a new proposal based on provided parameters
    """
    try:
        # Search for similar proposals
        similar_proposals = await vector_store.search(
            query=f"{params.client_name} {params.industry} {params.requirements}",
            k=3
        )
        
        # Generate proposal
        proposal_content = await proposal_generator.generate_proposal(
            params=params.dict(),
            similar_proposals=similar_proposals
        )
        
        # Generate both PDF and Markdown versions
        pdf_content = proposal_generator.export_to_pdf(proposal_content)
        markdown_content = proposal_generator.export_to_markdown(proposal_content)
        
        # Generate unique ID
        proposal_id = f"proposal_{params.client_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_path = data_dir / f"{proposal_id}.pdf"
        
        # Save PDF
        with open(output_path, "wb") as f:
            f.write(pdf_content)
        
        # Save proposal metadata
        proposal_data = {
            "id": proposal_id,
            "client_name": params.client_name,
            "industry": params.industry,
            "date": datetime.now().isoformat(),
            "status": "generated",
            "content": {
                "proposal": proposal_content,
                "markdown": markdown_content
            },
            "sections": {
                "requirements": params.requirements,
                "scope": params.scope,
                "timeline": params.timeline,
                "budget": params.budget
            },
            "filename": output_path.name,
            "similar_proposals": [p["metadata"]["id"] for p in similar_proposals if "id" in p["metadata"]]
        }
        save_proposal_metadata(proposal_id, proposal_data)
        
        # Add to vector store
        await vector_store.add_document(
            text=proposal_content,
            metadata={
                "id": proposal_id,
                "client_name": params.client_name,
                "industry": params.industry,
                "type": "generated"
            }
        )
        
        return proposal_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proposals", response_model=List[ProposalSummary])
async def list_proposals(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """List all proposals with pagination"""
    proposals = list_proposal_metadata(page, page_size)
    return [
        ProposalSummary(
            id=p["id"],
            client_name=p["client_name"],
            industry=p["industry"],
            date=p["date"],
            status=p["status"],
            filename=p.get("filename")
        )
        for p in proposals
    ]

@app.get("/proposals/{proposal_id}", response_model=ProposalDetail)
async def get_proposal(proposal_id: str):
    """Get detailed information about a specific proposal"""
    metadata = load_proposal_metadata(proposal_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return metadata

@app.post("/proposals/search", response_model=List[ProposalSummary])
async def search_proposals(query: SearchQuery):
    """Search for proposals using vector similarity and optional filters"""
    try:
        # Search in vector store
        results = await vector_store.search(
            query=query.query,
            k=query.page_size,
            filters=query.filters
        )
        
        # Get full metadata for each result
        proposals = []
        for result in results:
            if "id" in result["metadata"]:
                metadata = load_proposal_metadata(result["metadata"]["id"])
                if metadata:
                    proposals.append(ProposalSummary(
                        id=metadata["id"],
                        client_name=metadata["client_name"],
                        industry=metadata["industry"],
                        date=metadata["date"],
                        status=metadata["status"],
                        filename=metadata.get("filename")
                    ))
        
        return proposals
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_proposal(filename: str):
    """
    Download a generated proposal PDF
    """
    try:
        file_path = Path(f"./data/generated/{filename}")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BulkUploadResponse(BaseModel):
    """Response model for bulk upload"""
    processed_count: int
    successful_count: int
    failed_count: int
    proposal_ids: List[str]
    errors: Dict[str, str] = Field(default_factory=dict)


@app.post("/upload-proposals-bulk", response_model=BulkUploadResponse)
async def upload_proposals_bulk(
    files: List[UploadFile] = File(...),
    metadata: str = Form(...),
    session: Session = Depends(get_session)
):
    """
    Upload and process multiple PDF proposals in a single request
    """
    import json
    from concurrent.futures import ThreadPoolExecutor
    
    try:
        # Parse metadata
        metadata_dict = json.loads(metadata)
        proposal_metadata = ProposalMetadata(**metadata_dict)
        
        results = {
            "processed_count": len(files),
            "successful_count": 0,
            "failed_count": 0,
            "proposal_ids": [],
            "errors": {}
        }
        
        # Process each file
        for file in files:
            try:
                contents = await file.read()
                
                # Process PDF and extract text with metadata
                document = await pdf_processor.process_pdf(
                    pdf_content=contents,
                    session=session
                )
                
                # Set filename after document is created
                document.filename = file.filename
                session.commit()
                
                # Identify and extract sections
                semantic_blocks = await pdf_processor.identify_sections(
                    document=document,
                    session=session
                )
                
                # Organize sections by type
                sections = {}
                for block in semantic_blocks:
                    if block.confidence_score >= 0.7:  # Only include high-confidence blocks
                        sections[block.block_type.value] = {
                            "content": block.content,
                            "confidence": block.confidence_score
                        }
                
                # Extract key information
                extracted_info = await pdf_processor.extract_key_information(document, session)
                
                # Generate unique ID
                proposal_id = f"proposal_{proposal_metadata.client_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(results['proposal_ids'])}"
                
                # Add to vector store
                await vector_store.add_document(
                    text=document.content,
                    metadata={
                        "id": proposal_id,
                        "client_name": proposal_metadata.client_name,
                        "industry": proposal_metadata.industry,
                        "type": "uploaded",
                        "filename": file.filename
                    }
                )
                
                # Save proposal metadata
                proposal_data = {
                    "id": proposal_id,
                    "client_name": proposal_metadata.client_name,
                    "industry": proposal_metadata.industry,
                    "date": proposal_metadata.date,
                    "status": "uploaded",
                    "content": {
                        "full_text": document.content,
                        "summary": extracted_info.get("summary", "")
                    },
                    "sections": sections,
                    "filename": file.filename
                }
                save_proposal_metadata(proposal_id, proposal_data)
                
                results["successful_count"] += 1
                results["proposal_ids"].append(proposal_id)
                
            except Exception as e:
                results["failed_count"] += 1
                results["errors"][file.filename] = str(e)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
