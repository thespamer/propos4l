from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlmodel import Session
from typing import List, Optional
import io

from app.database import get_session
from app.models.database import Template, TemplateSection
from app.services.template_generator import TemplateGenerator
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateSectionResponse

router = APIRouter()

@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Create a new template from a PDF file
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Read file content
    pdf_content = await file.read()
    
    # Generate template
    try:
        template_generator = TemplateGenerator()
        template = await template_generator.generate_template_from_pdf(
            pdf_content=pdf_content,
            name=name,
            description=description,
            session=session
        )
        
        # Convert to response model
        sections = []
        for section in template.sections:
            sections.append(TemplateSectionResponse(
                id=section.id,
                name=section.name,
                content=section.content,
                order=section.order,
                metadata=section.metadata
            ))
        
        return TemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            creation_date=template.creation_date,
            structure=template.structure,
            sections=sections
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate template: {str(e)}"
        )

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(session: Session = Depends(get_session)):
    """
    List all available templates
    """
    templates = session.query(Template).all()
    
    result = []
    for template in templates:
        sections = []
        for section in template.sections:
            sections.append(TemplateSectionResponse(
                id=section.id,
                name=section.name,
                content=section.content,
                order=section.order,
                metadata=section.metadata
            ))
        
        result.append(TemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            creation_date=template.creation_date,
            structure=template.structure,
            sections=sections
        ))
    
    return result

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, session: Session = Depends(get_session)):
    """
    Get a specific template by ID
    """
    template = session.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    sections = []
    for section in template.sections:
        sections.append(TemplateSectionResponse(
            id=section.id,
            name=section.name,
            content=section.content,
            order=section.order,
            metadata=section.metadata
        ))
    
    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        creation_date=template.creation_date,
        structure=template.structure,
        sections=sections
    )

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: int, session: Session = Depends(get_session)):
    """
    Delete a template
    """
    template = session.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    # Delete all sections first
    session.query(TemplateSection).filter(TemplateSection.template_id == template_id).delete()
    
    # Delete template
    session.delete(template)
    session.commit()
