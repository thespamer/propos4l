from typing import List, Dict, Any, Optional, TypeVar, Generic, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from functools import partial
from collections import deque
import threading
from app.core.logging import get_logger
from app.core.monitoring import monitor_performance

T = TypeVar('T')
logger = get_logger(__name__)

class BatchProcessor(Generic[T]):
    """Generic batch processor for efficient data processing"""
    
    def __init__(self, batch_size: int = 10, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._queue = deque()
        self._lock = threading.Lock()
        
    @monitor_performance()
    def process_batch(self, items: List[T], process_func: Callable[[T], Any]) -> List[Any]:
        """Process a batch of items in parallel"""
        futures = []
        results = []
        
        for item in items:
            future = self.executor.submit(process_func, item)
            futures.append(future)
        
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing batch item: {str(e)}")
                results.append(None)
        
        return results
    
    def add_to_queue(self, item: T) -> None:
        """Add item to processing queue"""
        with self._lock:
            self._queue.append(item)
    
    def get_batch(self) -> List[T]:
        """Get next batch of items from queue"""
        items = []
        with self._lock:
            while len(items) < self.batch_size and self._queue:
                items.append(self._queue.popleft())
        return items

class VectorBatchProcessor:
    """Specialized processor for vector operations"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        
    @monitor_performance()
    def batch_encode(self, texts: List[str], encoder: Callable[[str], np.ndarray]) -> np.ndarray:
        """Encode texts in batches"""
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = [encoder(text) for text in batch]
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    @monitor_performance()
    def batch_similarity(self, query_vector: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """Compute similarities in batches"""
        similarities = []
        
        for i in range(0, len(vectors), self.batch_size):
            batch = vectors[i:i + self.batch_size]
            # Compute cosine similarity
            batch_similarities = np.dot(batch, query_vector) / (
                np.linalg.norm(batch, axis=1) * np.linalg.norm(query_vector)
            )
            similarities.extend(batch_similarities)
        
        return np.array(similarities)

class CacheManager:
    """Memory-efficient cache manager with LRU eviction"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._access_count: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self._lock:
            if key in self._cache:
                self._access_count[key] += 1
                return self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache with LRU eviction"""
        with self._lock:
            if len(self._cache) >= self.max_size:
                # Evict least recently used item
                min_key = min(self._access_count.items(), key=lambda x: x[1])[0]
                del self._cache[min_key]
                del self._access_count[min_key]
            
            self._cache[key] = value
            self._access_count[key] = 1
    
    def clear(self) -> None:
        """Clear cache"""
        with self._lock:
            self._cache.clear()
            self._access_count.clear()

class DatasetOptimizer:
    """Optimizer for large dataset operations"""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
    
    @monitor_performance()
    def optimize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Optimize embeddings for memory efficiency"""
        # Convert to float16 for memory efficiency while maintaining accuracy
        return embeddings.astype(np.float16)
    
    @monitor_performance()
    def chunk_dataset(self, data: List[Any]) -> List[List[Any]]:
        """Split dataset into manageable chunks"""
        return [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
    
    @monitor_performance()
    async def process_chunks(self, chunks: List[List[Any]], process_func: Callable) -> List[Any]:
        """Process chunks in parallel"""
        tasks = []
        for chunk in chunks:
            task = asyncio.create_task(process_func(chunk))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and flatten results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error processing chunk: {str(result)}")
            else:
                processed_results.extend(result)
        
        return processed_results
