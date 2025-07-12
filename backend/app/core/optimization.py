from typing import List, Dict, Any, Optional, TypeVar, Generic, Callable, Union
import asyncio
import gc
import itertools
import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial, wraps
from collections import deque
from queue import Queue
import threading
import numpy as np
from app.core.logging import get_logger
from app.core.monitoring import monitor_performance, get_system_metrics

T = TypeVar('T')
U = TypeVar('U')
logger = get_logger(__name__)

# Constants
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_BATCH_SIZE = 100
MAX_RETRIES = 3
MEMORY_THRESHOLD = 85  # percentage

@dataclass
class BatchStats:
    """Statistics for batch processing"""
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)

class BatchProcessor(Generic[T, U]):
    """Enhanced generic batch processor for efficient parallel data processing"""
    
    def __init__(
        self,
        batch_size: int = DEFAULT_BATCH_SIZE,
        max_workers: int = None,
        use_processes: bool = False,
        retry_failed: bool = True,
        max_retries: int = MAX_RETRIES
    ):
        self.batch_size = batch_size
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.retry_failed = retry_failed
        self.max_retries = max_retries
        
        # Use ProcessPoolExecutor for CPU-intensive tasks
        self.executor = (
            ProcessPoolExecutor(max_workers=self.max_workers)
            if use_processes else
            ThreadPoolExecutor(max_workers=self.max_workers)
        )
        
        self._queue: Queue[T] = Queue()
        self._lock = threading.Lock()
        self._stats = BatchStats()
        
    @monitor_performance(memory_threshold_mb=100)
    def process_batch(self, items: List[T], process_func: Callable[[T], U]) -> List[Optional[U]]:
        """Process a batch of items in parallel with error handling and retries"""
        if not items:
            return []
            
        self._stats.total_items += len(items)
        if not self._stats.start_time:
            self._stats.start_time = datetime.now()
        
        futures = []
        results: List[Optional[U]] = [None] * len(items)
        retry_items: List[Tuple[int, T, int]] = []  # (index, item, attempts)
        
        # Initial processing
        for i, item in enumerate(items):
            future = self.executor.submit(self._safe_process, process_func, item)
            futures.append((i, future))
        
        # Collect results
        for i, future in futures:
            try:
                result = future.result(timeout=30)  # 30-second timeout
                if isinstance(result, Exception):
                    if self.retry_failed:
                        retry_items.append((i, items[i], 1))
                    else:
                        self._handle_error(i, items[i], result)
                else:
                    results[i] = result
                    self._stats.successful_items += 1
            except Exception as e:
                if self.retry_failed:
                    retry_items.append((i, items[i], 1))
                else:
                    self._handle_error(i, items[i], e)
        
        # Retry failed items
        if retry_items and self.retry_failed:
            results = self._retry_failed_items(retry_items, results, process_func)
        
        self._stats.processed_items += len(items)
        
        # Check memory usage and trigger GC if needed
        metrics = get_system_metrics()
        if metrics.get('system', {}).get('memory', {}).get('percent', 0) > MEMORY_THRESHOLD:
            logger.warning("High memory usage detected, triggering garbage collection")
            gc.collect()
        
        return results
    
    def _safe_process(self, process_func: Callable[[T], U], item: T) -> Union[U, Exception]:
        """Safely execute the process function and return result or exception"""
        try:
            return process_func(item)
        except Exception as e:
            return e
    
    def _retry_failed_items(
        self,
        retry_items: List[Tuple[int, T, int]],
        results: List[Optional[U]],
        process_func: Callable[[T], U]
    ) -> List[Optional[U]]:
        """Retry failed items with exponential backoff"""
        while retry_items:
            next_retry = []
            futures = []
            
            for i, item, attempts in retry_items:
                if attempts >= self.max_retries:
                    self._handle_error(i, item, Exception(f"Max retries ({self.max_retries}) exceeded"))
                    continue
                    
                # Exponential backoff
                delay = 2 ** attempts
                asyncio.sleep(delay)
                
                future = self.executor.submit(self._safe_process, process_func, item)
                futures.append((i, future, attempts + 1))
            
            for i, future, next_attempt in futures:
                try:
                    result = future.result(timeout=30)
                    if isinstance(result, Exception):
                        next_retry.append((i, retry_items[i][1], next_attempt))
                    else:
                        results[i] = result
                        self._stats.successful_items += 1
                except Exception as e:
                    next_retry.append((i, retry_items[i][1], next_attempt))
            
            retry_items = next_retry
        
        return results
    
    def _handle_error(self, index: int, item: T, error: Exception) -> None:
        """Handle and log processing errors"""
        self._stats.failed_items += 1
        error_info = {
            'index': index,
            'item': str(item),
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat()
        }
        self._stats.errors.append(error_info)
        logger.error(
            f"Failed to process item {index}: {error}",
            extra={'error_info': error_info}
        )
    
    def add_to_queue(self, item: T) -> None:
        """Add item to processing queue"""
        self._queue.put(item)
    
    def add_many_to_queue(self, items: List[T]) -> None:
        """Add multiple items to processing queue"""
        for item in items:
            self._queue.put(item)
    
    def get_batch(self, timeout: Optional[float] = 1.0) -> List[T]:
        """Get next batch of items from queue with timeout"""
        items = []
        try:
            while len(items) < self.batch_size and not self._queue.empty():
                try:
                    item = self._queue.get(timeout=timeout)
                    items.append(item)
                except Exception:
                    break
        except Exception as e:
            logger.warning(f"Error getting batch from queue: {e}")
        return items
    
    def get_stats(self) -> BatchStats:
        """Get current processing statistics"""
        with self._lock:
            if self._stats.start_time and not self._stats.end_time:
                self._stats.end_time = datetime.now()
            return self._stats
    
    def clear_stats(self) -> None:
        """Reset processing statistics"""
        with self._lock:
            self._stats = BatchStats()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)

@dataclass
class VectorStats:
    """Statistics for vector operations"""
    total_vectors: int = 0
    processed_vectors: int = 0
    encoding_time: float = 0.0
    similarity_time: float = 0.0
    memory_usage: float = 0.0

class VectorBatchProcessor:
    """Enhanced processor for vector operations with memory optimization"""
    
    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE, precision: str = 'float32'):
        self.batch_size = batch_size
        self.precision = precision
        self.stats = VectorStats()
        self._executor = ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) + 4))
        
    @monitor_performance(memory_threshold_mb=500)
    def batch_encode(
        self,
        texts: List[str],
        encoder: Callable[[str], np.ndarray],
        normalize: bool = True
    ) -> np.ndarray:
        """Encode texts in batches with memory optimization and parallel processing"""
        start_time = time.perf_counter()
        self.stats.total_vectors = len(texts)
        
        # Process in parallel batches
        futures = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            future = self._executor.submit(self._encode_batch, batch, encoder)
            futures.append(future)
        
        # Collect results
        embeddings = []
        for future in futures:
            try:
                batch_embeddings = future.result(timeout=60)
                embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error encoding batch: {e}", exc_info=True)
        
        embeddings = np.array(embeddings, dtype=self.precision)
        self.stats.processed_vectors = len(embeddings)
        
        # Normalize if requested
        if normalize and len(embeddings) > 0:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            embeddings /= norms
        
        # Update stats
        self.stats.encoding_time = time.perf_counter() - start_time
        self.stats.memory_usage = embeddings.nbytes / (1024 * 1024)  # MB
        
        return embeddings
    
    def _encode_batch(self, batch: List[str], encoder: Callable[[str], np.ndarray]) -> List[np.ndarray]:
        """Encode a single batch of texts"""
        return [encoder(text) for text in batch]
    
    @monitor_performance(memory_threshold_mb=500)
    def batch_similarity(
        self,
        query_vector: np.ndarray,
        vectors: np.ndarray,
        metric: str = 'cosine',
        top_k: Optional[int] = None
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """Compute similarities in batches with multiple distance metrics"""
        start_time = time.perf_counter()
        
        if len(vectors) == 0:
            return np.array([]) if top_k is None else (np.array([]), np.array([]))
        
        # Ensure correct shapes and types
        query_vector = query_vector.astype(self.precision).reshape(1, -1)
        vectors = vectors.astype(self.precision)
        
        similarities = []
        for i in range(0, len(vectors), self.batch_size):
            batch = vectors[i:i + self.batch_size]
            
            if metric == 'cosine':
                # Compute cosine similarity
                batch_similarities = np.dot(batch, query_vector.T).flatten()
                if not np.all(np.isclose(np.linalg.norm(batch, axis=1), 1.0)):
                    # Normalize only if vectors aren't already normalized
                    batch_similarities /= (
                        np.linalg.norm(batch, axis=1) * np.linalg.norm(query_vector)
                    )
            elif metric == 'euclidean':
                # Compute euclidean distance
                batch_similarities = -np.linalg.norm(batch - query_vector, axis=1)
            elif metric == 'dot':
                # Compute dot product
                batch_similarities = np.dot(batch, query_vector.T).flatten()
            else:
                raise ValueError(f"Unsupported similarity metric: {metric}")
            
            similarities.extend(batch_similarities)
        
        similarities = np.array(similarities)
        
        # Update stats
        self.stats.similarity_time = time.perf_counter() - start_time
        
        if top_k is not None:
            # Get top-k results
            top_k = min(top_k, len(similarities))
            top_indices = np.argpartition(similarities, -top_k)[-top_k:]
            top_indices = top_indices[np.argsort(-similarities[top_indices])]
            return similarities[top_indices], top_indices
        
        return similarities

@dataclass
class CacheStats:
    """Statistics for cache operations"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    items_count: int = 0

class CacheManager:
    """Enhanced memory-efficient cache manager with LRU eviction and monitoring"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: Optional[float] = None):
        self.max_size = max_size
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024) if max_memory_mb else None
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, datetime] = {}
        self._lock = threading.Lock()
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with stats tracking"""
        with self._lock:
            if key in self._cache:
                self._access_times[key] = datetime.now()
                self.stats.hits += 1
                return self._cache[key]
            self.stats.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache with memory monitoring and LRU eviction"""
        with self._lock:
            # Check memory limit
            if self.max_memory_bytes:
                value_size = self._estimate_size(value)
                while (
                    self.stats.total_size_bytes + value_size > self.max_memory_bytes
                    and self._cache
                ):
                    self._evict_lru()
            
            # Check size limit
            while len(self._cache) >= self.max_size and self._cache:
                self._evict_lru()
            
            # Add new item
            self._cache[key] = value
            self._access_times[key] = datetime.now()
            self.stats.items_count = len(self._cache)
            
            # Update memory usage
            if self.max_memory_bytes:
                self.stats.total_size_bytes += self._estimate_size(value)
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self._cache:
            return
            
        lru_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        if self.max_memory_bytes:
            self.stats.total_size_bytes -= self._estimate_size(self._cache[lru_key])
        
        del self._cache[lru_key]
        del self._access_times[lru_key]
        self.stats.evictions += 1
        self.stats.items_count = len(self._cache)
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of an object"""
        if HAS_OBJSIZE:
            return objsize.get_deep_size(obj)
        else:
            # Rough estimation if objsize not available
            return sys.getsizeof(obj)
    
    def clear(self) -> None:
        """Clear cache and reset stats"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self.stats = CacheStats()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            hit_rate = (
                self.stats.hits / (self.stats.hits + self.stats.misses)
                if (self.stats.hits + self.stats.misses) > 0
                else 0
            )
            return {
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'hit_rate': hit_rate,
                'evictions': self.stats.evictions,
                'items_count': self.stats.items_count,
                'memory_usage_mb': self.stats.total_size_bytes / (1024 * 1024)
                if self.max_memory_bytes else None
            }

@dataclass
class DatasetStats:
    """Statistics for dataset operations"""
    total_items: int = 0
    processed_items: int = 0
    chunks_created: int = 0
    memory_saved: float = 0.0  # MB
    processing_time: float = 0.0

class DatasetOptimizer:
    """Enhanced optimizer for large dataset operations with memory management"""
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        self.chunk_size = chunk_size
        self.stats = DatasetStats()
        self._executor = ProcessPoolExecutor(max_workers=min(32, (os.cpu_count() or 1)))
    
    @monitor_performance(memory_threshold_mb=1000)
    def optimize_embeddings(
        self,
        embeddings: np.ndarray,
        precision: str = 'float16',
        compression: Optional[str] = None
    ) -> Union[np.ndarray, bytes]:
        """Optimize embeddings for memory efficiency with compression options"""
        start_time = time.perf_counter()
        original_size = embeddings.nbytes / (1024 * 1024)  # MB
        
        # Convert precision
        if precision == 'float16':
            optimized = embeddings.astype(np.float16)
        elif precision == 'bfloat16':
            # Custom bfloat16 conversion
            float32_view = embeddings.view(np.uint32)
            optimized = (float32_view >> 16).astype(np.uint16)
        else:
            optimized = embeddings.astype(precision)
        
        # Apply compression if requested
        if compression:
            if compression == 'zstd':
                import zstd
                optimized = zstd.compress(optimized.tobytes())
            elif compression == 'lz4':
                import lz4.frame
                optimized = lz4.frame.compress(optimized.tobytes())
            else:
                raise ValueError(f"Unsupported compression: {compression}")
        
        # Update stats
        final_size = (
            len(optimized) / (1024 * 1024)
            if isinstance(optimized, bytes)
            else optimized.nbytes / (1024 * 1024)
        )
        self.stats.memory_saved = original_size - final_size
        self.stats.processing_time = time.perf_counter() - start_time
        
        return optimized
    
    @monitor_performance()
    def chunk_dataset(
        self,
        data: Union[List[Any], np.ndarray],
        strategy: str = 'size',
        max_chunk_memory_mb: Optional[float] = None
    ) -> List[Union[List[Any], np.ndarray]]:
        """Split dataset into manageable chunks with multiple strategies"""
        self.stats.total_items = len(data)
        chunks = []
        
        if strategy == 'size':
            # Fixed size chunks
            for i in range(0, len(data), self.chunk_size):
                chunks.append(data[i:i + self.chunk_size])
        elif strategy == 'memory':
            if not max_chunk_memory_mb:
                raise ValueError("max_chunk_memory_mb required for memory strategy")
            
            if isinstance(data, np.ndarray):
                # Calculate items per chunk based on memory limit
                item_size = data[0].nbytes
                items_per_chunk = int((max_chunk_memory_mb * 1024 * 1024) / item_size)
                
                for i in range(0, len(data), items_per_chunk):
                    chunks.append(data[i:i + items_per_chunk])
            else:
                # Estimate size for Python objects
                current_chunk = []
                current_size = 0
                
                for item in data:
                    item_size = self._estimate_size(item)
                    if current_size + item_size > max_chunk_memory_mb * 1024 * 1024:
                        chunks.append(current_chunk)
                        current_chunk = [item]
                        current_size = item_size
                    else:
                        current_chunk.append(item)
                        current_size += item_size
                
                if current_chunk:
                    chunks.append(current_chunk)
        else:
            raise ValueError(f"Unsupported chunking strategy: {strategy}")
        
        self.stats.chunks_created = len(chunks)
        return chunks
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of an object"""
        if HAS_OBJSIZE:
            return objsize.get_deep_size(obj)
        return sys.getsizeof(obj)
    
    @monitor_performance(memory_threshold_mb=1000)
    async def process_chunks(
        self,
        chunks: List[Union[List[Any], np.ndarray]],
        process_func: Callable,
        max_concurrent: Optional[int] = None,
        show_progress: bool = False
    ) -> List[Any]:
        """Process chunks in parallel with improved error handling and progress tracking"""
        start_time = time.perf_counter()
        max_concurrent = max_concurrent or min(32, (os.cpu_count() or 1) * 2)
        semaphore = asyncio.Semaphore(max_concurrent)
        processed_results = []
        
        async def process_chunk(chunk: Union[List[Any], np.ndarray]) -> None:
            async with semaphore:
                try:
                    if asyncio.iscoroutinefunction(process_func):
                        result = await process_func(chunk)
                    else:
                        # Run CPU-bound function in executor
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(
                            self._executor, process_func, chunk
                        )
                    
                    processed_results.extend(result if isinstance(result, list) else [result])
                    self.stats.processed_items += len(chunk)
                    
                    if show_progress:
                        progress = self.stats.processed_items / self.stats.total_items * 100
                        logger.info(f"Processing progress: {progress:.1f}%")
                        
                except Exception as e:
                    logger.error(
                        f"Error processing chunk: {str(e)}",
                        exc_info=True
                    )
        
        # Process all chunks
        await asyncio.gather(
            *(process_chunk(chunk) for chunk in chunks)
        )
        
        self.stats.processing_time = time.perf_counter() - start_time
        return processed_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dataset optimization statistics"""
        return {
            'total_items': self.stats.total_items,
            'processed_items': self.stats.processed_items,
            'chunks_created': self.stats.chunks_created,
            'memory_saved_mb': self.stats.memory_saved,
            'processing_time': self.stats.processing_time,
            'items_per_second': (
                self.stats.processed_items / self.stats.processing_time
                if self.stats.processing_time > 0 else 0
            )
        }
