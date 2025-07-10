import time
import psutil
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger(__name__)

class PerformanceMetrics:
    def __init__(self):
        self.metrics = {}
        self._start_times = {}
        
    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation"""
        self._start_times[operation_name] = time.perf_counter()
        
    def end_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> float:
        """End timing an operation and record metrics"""
        if operation_name not in self._start_times:
            logger.warning(f"No start time found for operation: {operation_name}")
            return 0.0
            
        end_time = time.perf_counter()
        duration = end_time - self._start_times[operation_name]
        
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
            
        metric = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
            'cpu_percent': psutil.Process().cpu_percent()
        }
        
        if metadata:
            metric.update(metadata)
            
        self.metrics[operation_name].append(metric)
        return duration
        
    def get_metrics(self, operation_name: Optional[str] = None) -> Dict:
        """Get metrics for a specific operation or all operations"""
        if operation_name:
            return self.metrics.get(operation_name, [])
        return self.metrics
        
    def get_average_duration(self, operation_name: str) -> float:
        """Get average duration for an operation"""
        if operation_name not in self.metrics:
            return 0.0
        durations = [m['duration'] for m in self.metrics[operation_name]]
        return sum(durations) / len(durations)
        
    def clear_metrics(self, operation_name: Optional[str] = None) -> None:
        """Clear metrics for a specific operation or all operations"""
        if operation_name:
            self.metrics.pop(operation_name, None)
        else:
            self.metrics.clear()

# Global metrics instance
performance_metrics = PerformanceMetrics()

def monitor_performance(operation_name: Optional[str] = None, include_args: bool = False):
    """
    Decorator to monitor performance of functions
    
    Args:
        operation_name: Name of the operation (defaults to function name)
        include_args: Whether to include function arguments in metrics
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            metadata = {}
            
            if include_args:
                # Only include simple types in metadata
                arg_values = {
                    f"arg_{i}": str(arg)[:100] 
                    for i, arg in enumerate(args) 
                    if isinstance(arg, (str, int, float, bool))
                }
                kwarg_values = {
                    k: str(v)[:100]
                    for k, v in kwargs.items()
                    if isinstance(v, (str, int, float, bool))
                }
                metadata.update({
                    'args': arg_values,
                    'kwargs': kwarg_values
                })
            
            performance_metrics.start_operation(op_name)
            try:
                result = await func(*args, **kwargs)
                duration = performance_metrics.end_operation(op_name, metadata)
                logger.debug(f"{op_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                metadata['error'] = str(e)
                performance_metrics.end_operation(op_name, metadata)
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            metadata = {}
            
            if include_args:
                # Only include simple types in metadata
                arg_values = {
                    f"arg_{i}": str(arg)[:100] 
                    for i, arg in enumerate(args) 
                    if isinstance(arg, (str, int, float, bool))
                }
                kwarg_values = {
                    k: str(v)[:100]
                    for k, v in kwargs.items()
                    if isinstance(v, (str, int, float, bool))
                }
                metadata.update({
                    'args': arg_values,
                    'kwargs': kwarg_values
                })
            
            performance_metrics.start_operation(op_name)
            try:
                result = func(*args, **kwargs)
                duration = performance_metrics.end_operation(op_name, metadata)
                logger.debug(f"{op_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                metadata['error'] = str(e)
                performance_metrics.end_operation(op_name, metadata)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def get_system_metrics() -> Dict[str, float]:
    """Get current system metrics"""
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_available': psutil.virtual_memory().available / 1024 / 1024,  # MB
        'disk_usage': psutil.disk_usage('/').percent
    }
