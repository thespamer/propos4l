import faiss
import numpy as np
from typing import List, Dict, Optional, Tuple, Union
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path
from enum import Enum

from app.models.database import BlockType

class IndexType(str, Enum):
    DOCUMENT = "document"
    BLOCK = "block"

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: Optional[str] = None):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize or load FAISS indices
        self.indices = {}
        self.metadata = {}
        
        if index_path:
            self.index_path = Path(index_path)
            self.index_dir = self.index_path.parent
            
            # Load document index if exists
            doc_index_path = self.index_dir / "document_index.faiss"
            if doc_index_path.exists():
                self.indices[IndexType.DOCUMENT] = faiss.read_index(str(doc_index_path))
                with open(str(doc_index_path.with_suffix('.json')), 'r') as f:
                    self.metadata[IndexType.DOCUMENT] = json.load(f)
            else:
                self.indices[IndexType.DOCUMENT] = faiss.IndexFlatL2(self.dimension)
                self.metadata[IndexType.DOCUMENT] = []
            
            # Load block indices for each block type
            for block_type in BlockType:
                block_index_path = self.index_dir / f"block_{block_type.value}_index.faiss"
                if block_index_path.exists():
                    self.indices[block_type] = faiss.read_index(str(block_index_path))
                    with open(str(block_index_path.with_suffix('.json')), 'r') as f:
                        self.metadata[block_type] = json.load(f)
                else:
                    self.indices[block_type] = faiss.IndexFlatL2(self.dimension)
                    self.metadata[block_type] = []
        else:
            self.index_path = None
            self.index_dir = None
            # Initialize empty indices
            self.indices[IndexType.DOCUMENT] = faiss.IndexFlatL2(self.dimension)
            self.metadata[IndexType.DOCUMENT] = []
            for block_type in BlockType:
                self.indices[block_type] = faiss.IndexFlatL2(self.dimension)
                self.metadata[block_type] = []

    async def add_document(self, text: str, metadata: Dict):
        """
        Generate embedding for text and add document to vector store
        """
        # Generate embedding
        embedding = self.model.encode(text)
        embedding = embedding.reshape(1, -1)
        
        # Add to document index and metadata store
        self.indices[IndexType.DOCUMENT].add(embedding)
        self.metadata[IndexType.DOCUMENT].append(metadata)
        
        # Save indices if path is specified
        if self.index_path:
            self._save_indices()
    
    async def add_semantic_block(self, block_type: BlockType, content: str, metadata: Dict):
        """
        Add a semantic block to its type-specific index
        """
        # Generate embedding
        embedding = self.model.encode(content)
        embedding = embedding.reshape(1, -1)
        
        # Add to block-specific index and metadata store
        self.indices[block_type].add(embedding)
        self.metadata[block_type].append(metadata)
        
        # Save indices if path is specified
        if self.index_path:
            self._save_indices()

    async def search(self, 
        query: str, 
        k: int = 5, 
        index_type: Union[IndexType, BlockType] = IndexType.DOCUMENT,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents or blocks using a text query
        """
        # Generate query embedding
        query_embedding = self.model.encode(query)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search in the specified index
        distances, indices = self.indices[index_type].search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1:  # Valid index
                item = self.metadata[index_type][idx].copy()
                item['similarity_score'] = float(1 / (1 + distance))
                
                # Apply filters if specified
                if filters:
                    if all(item.get(key) == value for key, value in filters.items()):
                        results.append(item)
                else:
                    results.append(item)
                    
                if len(results) >= k:
                    break
        
        return results
    
    async def search_similar_blocks(self,
        content: str,
        block_type: BlockType,
        k: int = 5,
        confidence_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search for similar blocks of a specific type
        """
        # Generate content embedding
        content_embedding = self.model.encode(content)
        content_embedding = content_embedding.reshape(1, -1)
        
        # Search in the block-specific index
        distances, indices = self.indices[block_type].search(content_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1:  # Valid index
                similarity_score = float(1 / (1 + distance))
                if similarity_score >= confidence_threshold:
                    block = self.metadata[block_type][idx].copy()
                    block['similarity_score'] = similarity_score
                    results.append(block)
        
        return results
    
    def _save_indices(self):
        """
        Save all FAISS indices and metadata to disk
        """
        if self.index_path:
            # Save document index
            doc_index_path = self.index_dir / "document_index.faiss"
            faiss.write_index(self.indices[IndexType.DOCUMENT], str(doc_index_path))
            with open(str(doc_index_path.with_suffix('.json')), 'w') as f:
                json.dump(self.metadata[IndexType.DOCUMENT], f)
            
            # Save block indices
            for block_type in BlockType:
                block_index_path = self.index_dir / f"block_{block_type.value}_index.faiss"
                faiss.write_index(self.indices[block_type], str(block_index_path))
                with open(str(block_index_path.with_suffix('.json')), 'w') as f:
                    json.dump(self.metadata[block_type], f)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the vector store
        """
        stats = {
            "total_documents": len(self.metadata[IndexType.DOCUMENT])
        }
        
        # Add block type statistics
        for block_type in BlockType:
            stats[f"total_{block_type.value}_blocks"] = len(self.metadata[block_type])
        
        return stats
        
    def get_total_documents(self) -> int:
        """
        Get the total number of documents in the vector store
        """
        return len(self.metadata[IndexType.DOCUMENT])
