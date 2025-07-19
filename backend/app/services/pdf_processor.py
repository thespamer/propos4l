import fitz  # PyMuPDF
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from sqlmodel import Session
from sqlalchemy import select
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import hashlib
import json
import logging
import re
from collections import Counter
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.database import Document, SemanticBlock, BlockType
from app.database import get_session
from langchain_community.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.embeddings import OpenAIEmbeddings
from app.core.logging import get_logger
from app.core.monitoring import monitor_performance, performance_metrics, get_system_metrics
from app.services.nlp_service import NLPService
from app.core.optimization import BatchProcessor, VectorBatchProcessor, CacheManager, DatasetOptimizer

class PDFProcessor:
    def __init__(self, tesseract_path: Optional[str] = None, vector_store=None, batch_size: int = 5):
        """Initialize the PDF processor"""
        self.supported_formats = ['.pdf']
        self.logger = get_logger(__name__)
        self.vector_store = vector_store
        self.batch_size = batch_size
        self.nlp_service = NLPService()
        
        # Initialize optimizers
        self.batch_processor = BatchProcessor[str, dict](batch_size=batch_size)
        self.vector_processor = VectorBatchProcessor(batch_size=100)
        self.cache_manager = CacheManager(max_size=1000)
        self.dataset_optimizer = DatasetOptimizer(chunk_size=1000)
        
        # Configure Tesseract
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Configure logging
        self.logger = get_logger(__name__)
        
        # Initialize LangChain components with retry mechanism
        self.llm = OpenAI(temperature=0.3)  # Lower temperature for more consistent results
        
        # Initialize thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Initialize LRU cache for section identification
        self._init_caches()
        
        # Define section identification prompt
        self.section_prompt = PromptTemplate(
            input_variables=["text_chunk"],
            template="""Analyze the following text from a business proposal and identify any sections that match these categories:
            - Title: The main title or name of the proposal
            - Context: Background information and current situation
            - Problem: Description of the client's challenges or needs
            - Solution: Proposed solution or approach
            - Scope: Project scope and deliverables
            - Timeline: Project timeline or schedule
            - Investment: Pricing, costs, or budget information
            - Differentials: Company advantages or unique selling points

            Text to analyze: {text_chunk}
            
            Return a JSON object with the identified sections and their content. Only include sections that are clearly present in the text.
            Format: {{
                "section_name": "extracted_content",
                ...
            }}
            """
        )
        
        self.section_chain = LLMChain(llm=self.llm, prompt=self.section_prompt)
        self.vector_store = vector_store
        self.nlp_service = NLPService()
        
    def _init_caches(self):
        """Initialize LRU caches for various operations"""
        # Cache for section identification results
        self._identify_section_cache = lru_cache(maxsize=1000)(self._identify_section_uncached)
        # Cache for language pattern detection
        self._detect_language_patterns_cache = lru_cache(maxsize=500)(self._detect_language_patterns_uncached)
        # Cache for text extraction
        self._extract_text_cache = lru_cache(maxsize=100)(self._extract_text_uncached)
        
    @monitor_performance()
    async def extract_text(self, file_path: str) -> str:
        """Extract text from a PDF file with caching"""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Calculate hash for cache key
            content_hash = self._compute_file_hash(content)
            
            # Try to get from cache first
            return await self._extract_text_cache(content_hash, content)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    @monitor_performance()
    async def _extract_text_uncached(self, content_hash: str, content: bytes) -> str:
        """Extract text from PDF content without caching"""
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=content, filetype="pdf")
            
            text_content = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text from page
                text = page.get_text("text")
                
                # If no text found, try OCR
                if not text.strip():
                    # Convert PDF page to image
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Extract text using OCR
                    text = self._extract_text_from_image(img)
                
                text_content.append(text)
            
            doc.close()
            return "\n".join(text_content)
            
        except Exception as e:
            self.logger.error(f"Error in text extraction: {str(e)}")
            raise
        # Cache for formatting metadata
        self._extract_formatting_metadata_cache = lru_cache(maxsize=500)(self._extract_formatting_metadata_uncached)

    def _compute_file_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    def _extract_text_from_image(self, image: Image) -> str:
        """Extract text from an image using OCR"""
        try:
            return pytesseract.image_to_string(image)
        except Exception as e:
            self.logger.error(f"OCR error: {str(e)}")
            return ""
    
    def _detect_language_patterns_uncached(self, text: str) -> Dict:
        """Detect language patterns in the text (uncached version)"""
        try:
            patterns = {
                'bullet_points': len(re.findall(r'^[•\-\*]\s', text, re.MULTILINE)),
                'numbered_lists': len(re.findall(r'^\d+\.\s', text, re.MULTILINE)),
                'technical_terms': len(re.findall(r'\b(?:API|SDK|cloud|infrastructure|integration|implementation|deployment)\b', text, re.I)),
                'monetary_values': len(re.findall(r'(?:R\$|\$)\s*\d+(?:\.\d{3})*(?:,\d{2})?', text)),
                'dates': len(re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)),
                'percentages': len(re.findall(r'\d+(?:\.\d+)?%', text)),
                'sentence_count': len(re.findall(r'[.!?]+\s+', text)),
                'average_sentence_length': self._calculate_avg_sentence_length(text)
            }
            self.logger.debug(f"Language patterns detected: {patterns}")
            return patterns
        except Exception as e:
            self.logger.error(f"Error detecting language patterns: {str(e)}")
            return {}
            
    def _detect_language_patterns(self, text: str) -> Dict:
        """Cached wrapper for language pattern detection"""
        return self._detect_language_patterns_cache(text)
    
    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length"""
        sentences = re.split(r'[.!?]+\s+', text)
        if not sentences:
            return 0.0
        words = sum(len(re.findall(r'\w+', sentence)) for sentence in sentences)
        return words / len(sentences)
    
    def _extract_formatting_metadata_uncached(self, page: fitz.Page) -> Dict:
        """Extract formatting metadata from a PDF page (uncached version)"""
        try:
            metadata = {
                'text_blocks': [],
                'has_tables': False,
                'has_images': False,
                'layout_style': 'text'
            }
            
            # Extract text blocks with formatting
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_block = {
                                'text': span["text"],
                                'font': span["font"],
                                'size': span["size"],
                                'color': span["color"],
                                'bold': span["flags"] & 2 ** 3 != 0,
                                'italic': span["flags"] & 2 ** 1 != 0
                            }
                            metadata['text_blocks'].append(text_block)
                elif block["type"] == 1:  # Image block
                    metadata['has_images'] = True
            
            # Detect tables using heuristics
            if len(blocks) > 5:
                x_positions = [block["bbox"][0] for block in blocks if block["type"] == 0]
                y_positions = [block["bbox"][1] for block in blocks if block["type"] == 0]
                
                x_counts = Counter(x_positions)
                y_counts = Counter(y_positions)
                if any(count > 3 for count in x_counts.values()) or \
                   any(count > 3 for count in y_counts.values()):
                    metadata['has_tables'] = True
                    metadata['layout_style'] = 'table'
            
            # Determine overall layout style
            if metadata['has_images'] and len(metadata['text_blocks']) > 10:
                metadata['layout_style'] = 'mixed'
            elif metadata['has_images']:
                metadata['layout_style'] = 'image'
            
            self.logger.debug(f"Extracted formatting metadata for page with {len(metadata['text_blocks'])} text blocks")
            return metadata
        except Exception as e:
            self.logger.error(f"Error extracting formatting metadata: {str(e)}")
            return {'text_blocks': [], 'has_tables': False, 'has_images': False, 'layout_style': 'text'}
    
    def _extract_formatting_metadata(self, page: fitz.Page) -> Dict:
        """Cached wrapper for formatting metadata extraction"""
        # Use page number as part of cache key since pages are mutable
        return self._extract_formatting_metadata_cache(page.number)
        metadata['fonts'] = dict(metadata['fonts'])
        metadata['font_sizes'] = dict(metadata['font_sizes'])
        
        return metadata
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @monitor_performance(include_args=True)
    async def process_pdf(self, pdf_content: bytes, filename: str, session: Session):
        """Process PDF with optimized batch processing"""
        # Initialize document
        document = Document(filename=filename)
        session.add(document)
        await session.commit()
        
        try:
            # Load PDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            total_pages = len(pdf_document)
            
            # Process pages in optimized batches
            pages = list(range(total_pages))
            chunks = self.dataset_optimizer.chunk_dataset(pages)
            
            all_blocks = []
            for chunk in chunks:
                # Process chunk of pages in parallel
                page_results = self.batch_processor.process_batch(
                    [pdf_document[p] for p in chunk],
                    self._process_page
                )
                
                # Filter out None results and extract text
                valid_results = [r for r in page_results if r is not None]
                if valid_results:
                    texts, pattern_data, format_data = zip(*valid_results)
                    
                    # Create blocks for the chunk
                    chunk_blocks = await self._create_blocks(
                        document=document,
                        texts=texts,
                        pattern_data=pattern_data,
                        format_data=format_data,
                        session=session
                    )
                    all_blocks.extend(chunk_blocks)
            
            # Update document metadata
            document.content_length = sum(len(block.content) for block in all_blocks)
            document.processed = True
            await session.commit()
            
            # Process blocks in optimized batches
            await self.identify_sections(document, session)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {filename}: {str(e)}")
            raise
    
    @monitor_performance()
    def _process_page(self, page: fitz.Page, page_num: int) -> Optional[Tuple[str, Dict, Dict]]:
        """Process a single page of a PDF document"""
        try:
            # Try normal text extraction first
            text = page.get_text()
            
            # If no text found, try OCR
            if not text.strip():
                pil_image = Image.frombytes("RGB", [page.rect.width, page.rect.height], page.get_pixmap().samples)
                text = self._extract_text_from_image(pil_image)
            
            # Extract formatting metadata
            page_metadata = self._extract_formatting_metadata(page)
            
            # Detect language patterns
            patterns = self._detect_language_patterns(text)
            
            self.logger.debug(f"Successfully processed page {page_num}")
            return text, page_metadata, patterns
            
        except Exception as e:
            self.logger.error(f"Error processing page {page_num}: {str(e)}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @monitor_performance(include_args=True)
    async def identify_sections(self, document: Document, session: Session):
        """Identify sections with optimized batch processing"""
        try:
            # Get all blocks for the document
            blocks = await session.execute(
                select(SemanticBlock).where(SemanticBlock.document_id == document.id)
            )
            blocks = blocks.scalars().all()
            
            # Split blocks into chunks for processing
            chunks = self.dataset_optimizer.chunk_dataset(blocks)
            
            for chunk in chunks:
                # Process chunk of blocks in parallel
                texts = [block.content for block in chunk]
                section_results = self.batch_processor.process_batch(
                    texts,
                    self._identify_section_uncached
                )
                
                # Update blocks with section information
                for block, section_info in zip(chunk, section_results):
                    if section_info:
                        block.block_type = section_info.get('type', BlockType.UNKNOWN)
                        block.metadata['section_info'] = section_info
                
                await session.commit()
            
            return blocks
            
        except Exception as e:
            self.logger.error(f"Error identifying sections: {str(e)}")
            raise
    
    @monitor_performance()
    def _identify_section_uncached(self, chunk: str) -> Optional[Dict[str, str]]:
        """Process a single chunk to identify sections (uncached version)"""
        try:
            # Use LLM to identify section type and extract key info
            response = self.section_chain.run(chunk)
            section_info = json.loads(response)
            
            # Enhance section identification with NLP analysis
            key_phrases = self.nlp_service.extract_key_phrases(chunk, method='hybrid')
            technical_terms = self.nlp_service.extract_technical_terms(chunk)
            text_structure = self.nlp_service.analyze_text_structure(chunk)
            
            # Use text structure and technical terms to refine section type
            if text_structure['complexity_score'] > 0.7 and any(term['term'].lower() in ['architecture', 'implementation', 'solution'] 
                                                               for term in technical_terms):
                section_info['confidence'] = min(1.0, section_info.get('confidence', 0.8) + 0.1)
            
            # Add NLP insights to section info
            section_info['nlp_insights'] = {
                'key_phrases': key_phrases[:5],  # Top 5 key phrases
                'technical_terms': [term['term'] for term in technical_terms[:5]],  # Top 5 technical terms
                'complexity_score': text_structure['complexity_score']
            }
            
            return section_info
        except Exception as e:
            self.logger.error(f"Error identifying sections in chunk: {str(e)}")
            return None
    
    @monitor_performance()
    async def _get_block_metadata(self, content: str, document: Document, 
                                start_pos: int, end_pos: int, 
                                block_type: BlockType) -> Optional[Dict]:
        """Get all metadata for a block in parallel"""
        try:
            # Extract language patterns
            patterns = self._extract_language_patterns(content)
            
            # Extract formatting metadata
            formatting = self._extract_formatting_metadata(content)
            
            # Enhanced NLP analysis
            entities = self.nlp_service.extract_entities(content)
            key_phrases = self.nlp_service.extract_key_phrases(content)
            technical_terms = self.nlp_service.extract_technical_terms(content)
            text_structure = self.nlp_service.analyze_text_structure(content)
            
            return {
                'confidence_score': similarity_score,
                'language_patterns': patterns,
                'formatting_metadata': formatting
            }
            
        except Exception as e:
            self.logger.error(f"Error getting block metadata: {str(e)}")
            return None
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm1 * norm2)
    
    def _find_block_formatting(self, document: Document, start_pos: int, end_pos: int) -> Dict:
        """Extract formatting metadata for a specific block from document metadata"""
        doc_metadata = document.metadata.get('formatting', [])
        block_formatting = {
            'fonts': Counter(),
            'font_sizes': Counter(),
            'has_tables': False,
            'has_images': False,
            'layout_style': 'text'
        }
        
        # Combine formatting data from all pages that contain this block
        char_count = 0
        for page_metadata in doc_metadata:
            for block in page_metadata.get('text_blocks', []):
                text = block.get('text', '')
                block_start = char_count
                block_end = char_count + len(text)
                
                # Check if this block overlaps with our target block
                if not (block_end <= start_pos or block_start >= end_pos):
                    block_formatting['fonts'][block['font']] += 1
                    block_formatting['font_sizes'][block['size']] += 1
                    
                    if block.get('bold'):
                        block_formatting['has_bold'] = True
                    if block.get('italic'):
                        block_formatting['has_italic'] = True
                
                char_count += len(text)
            
            # Copy page-level attributes if they overlap with our block
            if page_metadata.get('has_tables'):
                block_formatting['has_tables'] = True
            if page_metadata.get('has_images'):
                block_formatting['has_images'] = True
            if page_metadata.get('layout_style') != 'text':
                block_formatting['layout_style'] = page_metadata['layout_style']
        
        # Convert Counters to regular dicts
        block_formatting['fonts'] = dict(block_formatting['fonts'])
        block_formatting['font_sizes'] = dict(block_formatting['font_sizes'])
        
        return block_formatting
