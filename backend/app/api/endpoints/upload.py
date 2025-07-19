from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import os
import shutil
import uuid
from datetime import datetime
import asyncio

from app.core.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.processing_status import create_pdf_processing_tracker
from app.db.session import SessionLocal

router = APIRouter()

@router.post("/upload")
async def upload_proposal(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    client_name: str = Form(None),
    industry: str = Form(None),
):
    """
    Upload one or multiple proposal PDFs for processing.
    Returns tracking IDs for monitoring processing progress.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate file types
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not a PDF"
            )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    results = []
    tracking_ids = []
    
    for file in files:
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            safe_filename = f"{timestamp}_{unique_id}_{file.filename.replace(' ', '_')}"
            file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create a processing tracker for this file
            tracker = create_pdf_processing_tracker(file.filename)
            tracking_ids.append(tracker.id)
            
            # Process file in background
            background_tasks.add_task(
                process_pdf_file,
                file_path=file_path,
                filename=file.filename,
                client_name=client_name,
                industry=industry,
                tracker_id=tracker.id
            )
            
            results.append({
                "filename": file.filename,
                "status": "processing",
                "tracking_id": tracker.id
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "message": f"Processing {len(files)} file(s)",
        "results": results,
        "tracking_ids": tracking_ids
    }

async def process_pdf_file(
    file_path: str,
    filename: str,
    client_name: Optional[str],
    industry: Optional[str],
    tracker_id: str
):
    """
    Process a PDF file in the background with progress tracking.
    """
    from app.services.processing_status import get_tracker
    
    # Get the tracker
    tracker = get_tracker(tracker_id)
    if not tracker:
        print(f"Error: Tracker {tracker_id} not found")
        return
    
    # Create a new database session
    async with SessionLocal() as session:
        try:
            # Start processing
            processor = PDFProcessor()
            
            # Step 1: Extract text
            await tracker.start_next_step(f"Iniciando extração de texto de {filename}")
            text_content = await processor.extract_text(file_path)
            await tracker.complete_current_step(f"Extraído {len(text_content)} caracteres")
            await asyncio.sleep(0.5)  # Small delay for UI updates
            
            # Step 2: Create Document and identify sections
            await tracker.start_next_step("Analisando estrutura do documento")
            document = Document(filename=filename, content=text_content)
            session.add(document)
            await session.commit()
            sections = await processor.identify_sections(document, session)
            section_count = len(sections) if sections else 0
            await tracker.complete_current_step(f"Identificadas {section_count} seções")
            await asyncio.sleep(0.5)
            
            # Step 3: Extract key information
            await tracker.start_next_step("Extraindo informações-chave")
            keywords = await processor.extract_keywords(text_content)
            entities = await processor.extract_entities(text_content)
            info_count = len(keywords) + len(entities)
            await tracker.complete_current_step(f"Extraídas {info_count} informações-chave")
            await asyncio.sleep(0.5)
            
            # Step 4: Vector indexing
            await tracker.start_next_step("Indexando conteúdo para busca semântica")
            await processor.index_content(text_content, file_path)
            await tracker.complete_current_step("Indexação concluída")
            await asyncio.sleep(0.5)
            
            # Step 5: Store metadata
            await tracker.start_next_step("Armazenando metadados")
            metadata = {
                "filename": filename,
                "client_name": client_name,
                "industry": industry,
                "upload_time": datetime.now().isoformat(),
                "file_path": file_path,
                "section_count": section_count,
                "keyword_count": len(keywords),
                "entity_count": len(entities)
            }
            await processor.store_metadata(file_path, metadata)
            await tracker.complete_current_step("Metadados armazenados")
            await asyncio.sleep(0.5)
            
            # Step 6: Finalization
            await tracker.start_next_step("Finalizando processamento")
            # Any final processing steps here
            await tracker.complete_current_step("Documento pronto para uso")
            
            # Mark processing as complete
            await tracker.complete_processing()
            
        except Exception as e:
            # If any step fails, mark the current step as failed
            if tracker.get_current_step():
                await tracker.fail_current_step(e, f"Erro: {str(e)}")
            await tracker.complete_processing()
            print(f"Error processing {filename}: {str(e)}")
