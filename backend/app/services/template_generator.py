from pathlib import Path
import json
from typing import Dict, List, Optional, Any
from sqlmodel import Session
import os

from app.models.database import Document, Template, TemplateSection
from app.services.pdf_processor import PDFProcessor
from app.core.logging import get_logger
from app.database import get_session


class TemplateGenerator:
    def __init__(self, pdf_processor: Optional[PDFProcessor] = None):
        """Initialize the template generator service"""
        self.logger = get_logger(__name__)
        self.pdf_processor = pdf_processor or PDFProcessor()
        self.template_storage_path = Path("/app/storage/templates")
        
        # Ensure template storage directory exists
        os.makedirs(self.template_storage_path, exist_ok=True)
    
    async def generate_template_from_pdf(self, pdf_content: bytes, name: str, description: str, session: Session) -> Template:
        """
        Generate a template from a PDF document
        
        Args:
            pdf_content: The binary content of the PDF
            name: Name for the template
            description: Description of the template
            session: Database session
            
        Returns:
            The created template object
        """
        try:
            # Process the PDF to extract document and sections
            document = await self.pdf_processor.process_pdf(
            pdf_content=pdf_content,
            filename=f"{name}.pdf",
            session=session
        )
            
            # Identify sections in the document
            await self.pdf_processor.identify_sections(document, session)
            
            # Create a new template
            template = Template(
                name=name,
                description=description,
                source_document_id=document.id,
                structure={}
            )
            
            session.add(template)
            session.commit()
            session.refresh(template)
            
            # Extract sections from the document and create template sections
            template_structure = {}
            template_sections = []
            
            # Get all semantic blocks from the document
            blocks = session.query(document.semantic_blocks).all()
            
            for block in blocks:
                # Only include blocks with identified types (skip unknown)
                if block.block_type and block.block_type != "UNKNOWN":
                    section = TemplateSection(
                        template_id=template.id,
                        name=block.block_type,
                        content=block.content,
                        order=len(template_sections),
                        metadata={
                            "source_position": block.position,
                            "confidence_score": block.metadata.get("confidence_score", 0.0) if block.metadata else 0.0
                        }
                    )
                    
                    template_sections.append(section)
                    
                    # Add to structure for easy reference
                    template_structure[block.block_type] = {
                        "id": len(template_sections) - 1,
                        "required": True if block.block_type in ["TITLE", "SOLUTION", "INVESTMENT"] else False
                    }
            
            # Add sections to database
            session.add_all(template_sections)
            
            # Update template structure
            template.structure = template_structure
            session.commit()
            session.refresh(template)
            
            # Save template to file system for backup
            template_path = self.template_storage_path / f"{template.id}.json"
            with open(template_path, "w") as f:
                template_data = {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "structure": template.structure,
                    "sections": [
                        {
                            "name": section.name,
                            "content": section.content,
                            "order": section.order,
                            "metadata": section.metadata
                        }
                        for section in template_sections
                    ]
                }
                json.dump(template_data, f, indent=2)
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error generating template from PDF: {str(e)}")
            session.rollback()
            raise
