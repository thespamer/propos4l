import time
import asyncio
import functools
import gc
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List, Set, Union

from app.core.logging import get_logger

# Try to import optional monitoring dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import objsize
    HAS_OBJSIZE = True
except ImportError:
    HAS_OBJSIZE = False

logger = get_logger(__name__)

# Constants
METRIC_RETENTION_DAYS = 7
METRIC_CLEANUP_INTERVAL = 3600  # 1 hour
METRIC_AGGREGATION_INTERVAL = 300  # 5 minutes
MEMORY_WARNING_THRESHOLD = 85  # percentage
CPU_WARNING_THRESHOLD = 80  # percentage
IO_WARNING_THRESHOLD = 70  # percentage
NETWORK_WARNING_THRESHOLD = 75  # percentage
DISK_WARNING_THRESHOLD = 90  # percentage
ALERT_COOLDOWN = 300  # 5 minutes between repeated alerts
METRIC_SAMPLE_INTERVAL = 60  # 1 minute between detailed samples
METRIC_BATCH_SIZE = 100  # Number of metrics to process in batch

@dataclass
class ResourceUsage:
    """System resource usage metrics"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_rss: float = 0.0  # MB
    io_read_mb: float = 0.0
    io_write_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    disk_usage: float = 0.0
    thread_count: int = 0
    open_files: int = 0
    open_connections: int = 0

@dataclass
class MetricPoint:
    """Enhanced metric point with detailed resource tracking"""
    timestamp: datetime
    duration: float
    operation: str
    success: bool = True
    error: Optional[str] = None
    memory_usage: Optional[float] = None
    cpu_percent: Optional[float] = None
    thread_id: Optional[int] = None
    coroutine_id: Optional[int] = None
    resources: Optional[ResourceUsage] = None
    gc_stats: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric point to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'duration': round(self.duration, 3),
            'operation': self.operation,
            'success': self.success,
            'error': self.error,
            'memory_mb': round(self.memory_usage, 2) if self.memory_usage else None,
            'cpu_percent': round(self.cpu_percent, 1) if self.cpu_percent else None,
            'thread_id': self.thread_id,
            'coroutine_id': self.coroutine_id,
            'resources': vars(self.resources) if self.resources else None,
            'gc_stats': self.gc_stats,
            'metadata': self.metadata
        }

@dataclass
class MetricSummary:
    """Summary statistics for an operation"""
    count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_memory_mb: float = 0.0
    avg_cpu_percent: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None

class PerformanceMetrics:
    """Enhanced performance metrics manager with aggregation and alerting"""
    
    def __init__(self):
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self._start_times: Dict[str, Dict[int, float]] = {}
        self._operation_summaries: Dict[str, MetricSummary] = {}
        self._resource_samples: List[ResourceUsage] = []
        self._last_alerts: Dict[str, datetime] = {}
        self._last_sample = datetime.now()
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._last_cleanup = datetime.now()
        self._last_aggregation = datetime.now()
        
        # Start background cleanup task
        asyncio.create_task(self._periodic_cleanup())
        
    async def _periodic_cleanup(self) -> None:
        """Periodically clean up old metrics"""
        while True:
            try:
                await asyncio.sleep(METRIC_CLEANUP_INTERVAL)
                self.cleanup_old_metrics()
            except Exception as e:
                logger.error(f"Error in metric cleanup: {e}")
                
    def cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period"""
        with self._lock:
            cutoff = datetime.now() - timedelta(days=METRIC_RETENTION_DAYS)
            for op_name in list(self.metrics.keys()):
                self.metrics[op_name] = [
                    m for m in self.metrics[op_name]
                    if m.timestamp > cutoff
                ]
                if not self.metrics[op_name]:
                    del self.metrics[op_name]
        
    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation with thread-specific timing"""
        thread_id = threading.get_ident()
        if operation_name not in self._start_times:
            self._start_times[operation_name] = {}
        self._start_times[operation_name][thread_id] = time.perf_counter()
        
    def end_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None, error: Optional[Exception] = None) -> float:
        """Enhanced operation completion tracking with error handling and resource monitoring"""
        thread_id = threading.get_ident()
        
        if operation_name not in self._start_times or thread_id not in self._start_times[operation_name]:
            logger.warning(f"No start time found for operation '{operation_name}' in thread {thread_id}")
            return 0.0
            
        end_time = time.perf_counter()
        duration = end_time - self._start_times[operation_name][thread_id]
        
        # Collect metrics in a thread-safe way
        with self._lock:
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
                self._operation_summaries[operation_name] = MetricSummary()
            
            # Create metric point with enhanced tracking
            metric_point = MetricPoint(
                timestamp=datetime.now(),
                duration=duration,
                operation=operation_name,
                thread_id=thread_id,
                coroutine_id=id(asyncio.current_task()) if asyncio.current_task() else None,
                success=error is None,
                error=str(error) if error else None,
                gc_stats={
                    'collections': gc.get_count(),
                    'objects': len(gc.get_objects())
                },
                metadata=metadata or {}
            )
            
            # Update operation summary
            summary = self._operation_summaries[operation_name]
            summary.count += 1
            if error:
                summary.error_count += 1
                summary.last_error = str(error)
                summary.last_error_time = datetime.now()
            else:
                summary.success_count += 1
            summary.total_duration += duration
            summary.min_duration = min(summary.min_duration, duration)
            summary.max_duration = max(summary.max_duration, duration)
            
            # Collect comprehensive system metrics
            def collect_system_metrics():
                if HAS_PSUTIL:
                    try:
                        process = psutil.Process()
                        current_time = datetime.now()
                        
                        # Basic process metrics
                        metric_point.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                        metric_point.cpu_percent = process.cpu_percent()
                        
                        # Detailed resource tracking
                        resources = ResourceUsage(
                            cpu_percent=process.cpu_percent(),
                            memory_percent=process.memory_percent(),
                            memory_rss=process.memory_info().rss / 1024 / 1024,
                            thread_count=process.num_threads(),
                            open_files=len(process.open_files()),
                            open_connections=len(process.connections())
                        )
                        
                        # IO metrics if available
                        if hasattr(process, 'io_counters'):
                            io = process.io_counters()
                            resources.io_read_mb = io.read_bytes / 1024 / 1024
                            resources.io_write_mb = io.write_bytes / 1024 / 1024
                        
                        # Network metrics if available
                        if psutil.net_io_counters():
                            net = psutil.net_io_counters()
                            resources.network_sent_mb = net.bytes_sent / 1024 / 1024
                            resources.network_recv_mb = net.bytes_recv / 1024 / 1024
                        
                        # Disk usage
                        resources.disk_usage = psutil.disk_usage('/').percent
                        
                        metric_point.resources = resources
                        
                        # Check for periodic detailed sampling
                        if (current_time - self._last_sample).total_seconds() >= METRIC_SAMPLE_INTERVAL:
                            self._resource_samples.append(resources)
                            self._last_sample = current_time
                            
                            # Keep only recent samples
                            max_samples = 24 * 60  # 24 hours of minute samples
                            if len(self._resource_samples) > max_samples:
                                self._resource_samples = self._resource_samples[-max_samples:]
                        
                        # Update summary statistics
                        summary = self._operation_summaries[operation_name]
                        summary.avg_memory_mb = (
                            (summary.avg_memory_mb * (summary.count - 1) + metric_point.memory_usage)
                            / summary.count
                        )
                        summary.avg_cpu_percent = (
                            (summary.avg_cpu_percent * (summary.count - 1) + metric_point.cpu_percent)
                            / summary.count
                        )
                        
                        # Check thresholds and send alerts
                        self._check_thresholds(resources, operation_name)
                        
                        # Check for high resource usage
                        if metric_point.memory_usage > MEMORY_WARNING_THRESHOLD:
                            logger.warning(
                                f"High memory usage detected in {operation_name}: "
                                f"{metric_point.memory_usage:.1f}MB"
                            )
                        if metric_point.cpu_percent > CPU_WARNING_THRESHOLD:
                            logger.warning(
                                f"High CPU usage detected in {operation_name}: "
                                f"{metric_point.cpu_percent:.1f}%"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to get psutil metrics: {e}")
                        
                if HAS_OBJSIZE:
                    try:
                        # Sample memory usage of local variables
                        frame = sys._getframe(2)  # Get caller's frame
                        local_vars_size = sum(
                            objsize.get_deep_size(value)
                            for value in frame.f_locals.values()
                        )
                        if metadata is None:
                            metadata = {}
                        metadata['local_vars_size_mb'] = local_vars_size / 1024 / 1024
                    except Exception as e:
                        logger.warning(f"Failed to measure object sizes: {e}")
            
            # Run system metric collection in thread pool
            self._executor.submit(collect_system_metrics)
            
            if metadata:
                metric_point.metadata.update(metadata)
            
            self.metrics[operation_name].append(metric_point)
            
            # Cleanup old metrics if needed
            if (datetime.now() - self._last_cleanup).total_seconds() > METRIC_CLEANUP_INTERVAL:
                self.cleanup_old_metrics()
                self._last_cleanup = datetime.now()
            
        return duration
        
    def get_metrics(self, operation_name: Optional[str] = None, window_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Get enhanced metrics with filtering and summary statistics"""
        with self._lock:
            result = {
                'timestamp': datetime.now().isoformat(),
                'metrics': {},
                'summaries': {},
                'system_stats': self._get_system_stats()
            }
            
            # Filter metrics by time window if specified
            if window_minutes:
                cutoff = datetime.now() - timedelta(minutes=window_minutes)
            
            # Get metrics and summaries
            ops = [operation_name] if operation_name else self.metrics.keys()
            for op in ops:
                if op in self.metrics:
                    metrics = self.metrics[op]
                    if window_minutes:
                        metrics = [m for m in metrics if m.timestamp > cutoff]
                    
                    result['metrics'][op] = [m.to_dict() for m in metrics]
                    
                    if op in self._operation_summaries:
                        summary = self._operation_summaries[op]
                        result['summaries'][op] = {
                            'total_calls': summary.count,
                            'success_rate': (
                                summary.success_count / summary.count
                                if summary.count > 0 else 0
                            ),
                            'avg_duration': (
                                summary.total_duration / summary.count
                                if summary.count > 0 else 0
                            ),
                            'min_duration': (
                                summary.min_duration
                                if summary.min_duration != float('inf') else 0
                            ),
                            'max_duration': summary.max_duration,
                            'avg_memory_mb': summary.avg_memory_mb,
                            'avg_cpu_percent': summary.avg_cpu_percent,
                            'last_error': summary.last_error,
                            'last_error_time': (
                                summary.last_error_time.isoformat()
                                if summary.last_error_time else None
                            )
                        }
            
            return result.copy()
        
    def get_average_duration(self, operation_name: str, window_minutes: Optional[int] = None) -> float:
        """Get average duration for an operation with optional time window"""
        with self._lock:
            if operation_name not in self.metrics:
                return 0.0
                
            metrics = self.metrics[operation_name]
            if window_minutes:
                cutoff = datetime.now() - timedelta(minutes=window_minutes)
                metrics = [m for m in metrics if m.timestamp > cutoff]
                
            if not metrics:
                return 0.0
                
            return sum(m.duration for m in metrics) / len(metrics)
        
    def clear_metrics(self, operation_name: Optional[str] = None) -> None:
        """Clear metrics for a specific operation or all operations with thread safety"""
        with self._lock:
            if operation_name:
                self.metrics.pop(operation_name, None)
                self._start_times.pop(operation_name, None)
            else:
                self.metrics.clear()
                self._start_times.clear()
                
    def _check_thresholds(self, resources: ResourceUsage, operation_name: str) -> None:
        """Check resource thresholds and emit warnings with cooldown"""
        current_time = datetime.now()
        alerts = []
        
        def can_alert(alert_type: str) -> bool:
            if alert_type not in self._last_alerts:
                return True
            return (current_time - self._last_alerts[alert_type]).total_seconds() >= ALERT_COOLDOWN
        
        # Check CPU usage
        if resources.cpu_percent > CPU_WARNING_THRESHOLD and can_alert('cpu'):
            alerts.append(f"High CPU usage: {resources.cpu_percent:.1f}%")
            self._last_alerts['cpu'] = current_time
        
        # Check memory usage
        if resources.memory_percent > MEMORY_WARNING_THRESHOLD and can_alert('memory'):
            alerts.append(f"High memory usage: {resources.memory_percent:.1f}%")
            self._last_alerts['memory'] = current_time
        
        # Check disk usage
        if resources.disk_usage > DISK_WARNING_THRESHOLD and can_alert('disk'):
            alerts.append(f"High disk usage: {resources.disk_usage:.1f}%")
            self._last_alerts['disk'] = current_time
        
        # Check IO usage if metrics available
        if resources.io_read_mb + resources.io_write_mb > 0:
            io_rate = (resources.io_read_mb + resources.io_write_mb) / METRIC_SAMPLE_INTERVAL
            if io_rate > IO_WARNING_THRESHOLD and can_alert('io'):
                alerts.append(f"High IO rate: {io_rate:.1f} MB/s")
                self._last_alerts['io'] = current_time
        
        # Check network usage if metrics available
        if resources.network_sent_mb + resources.network_recv_mb > 0:
            net_rate = (resources.network_sent_mb + resources.network_recv_mb) / METRIC_SAMPLE_INTERVAL
            if net_rate > NETWORK_WARNING_THRESHOLD and can_alert('network'):
                alerts.append(f"High network rate: {net_rate:.1f} MB/s")
                self._last_alerts['network'] = current_time
        
        # Log alerts with operation context
        for alert in alerts:
            logger.warning(
                f"{alert} during operation '{operation_name}'",
                extra={
                    'operation': operation_name,
                    'resources': vars(resources)
                }
            )
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get aggregated system statistics"""
        if not self._resource_samples:
            return {}
            
        # Calculate stats over recent samples
        recent_samples = self._resource_samples[-60:]  # Last hour of minute samples
        return {
            'cpu_percent': {
                'current': recent_samples[-1].cpu_percent,
                'avg': sum(s.cpu_percent for s in recent_samples) / len(recent_samples),
                'max': max(s.cpu_percent for s in recent_samples)
            },
            'memory_percent': {
                'current': recent_samples[-1].memory_percent,
                'avg': sum(s.memory_percent for s in recent_samples) / len(recent_samples),
                'max': max(s.memory_percent for s in recent_samples)
            },
            'disk_usage': recent_samples[-1].disk_usage,
            'thread_count': recent_samples[-1].thread_count,
            'open_files': recent_samples[-1].open_files,
            'open_connections': recent_samples[-1].open_connections
        }
    
    def get_slow_operations(self, threshold_seconds: float = 1.0, window_minutes: Optional[int] = 60) -> Dict[str, Any]:
        """Get detailed analysis of slow operations"""
        slow_ops = {}
        cutoff = datetime.now() - timedelta(minutes=window_minutes) if window_minutes else None
        
        with self._lock:
            for op_name, metrics in self.metrics.items():
                # Filter by time window if specified
                op_metrics = [
                    m for m in metrics
                    if (not cutoff or m.timestamp > cutoff) and m.duration > threshold_seconds
                ]
                
                if op_metrics:
                    slow_ops[op_name] = {
                        'count': len(op_metrics),
                        'avg_duration': sum(m.duration for m in op_metrics) / len(op_metrics),
                        'max_duration': max(m.duration for m in op_metrics),
                        'avg_memory': (
                            sum(m.memory_usage for m in op_metrics if m.memory_usage)
                            / len([m for m in op_metrics if m.memory_usage])
                            if any(m.memory_usage for m in op_metrics) else None
                        ),
                        'samples': [
                            {
                                'timestamp': m.timestamp.isoformat(),
                                'duration': m.duration,
                                'memory_mb': m.memory_usage,
                                'cpu_percent': m.cpu_percent,
                                'metadata': m.metadata
                            }
                            for m in sorted(op_metrics, key=lambda x: x.duration, reverse=True)[:10]
                        ]
                    }
        
        return sorted(slow_ops, key=lambda x: x['avg_duration'], reverse=True)

# Global metrics instance
performance_metrics = PerformanceMetrics()

def monitor_performance(
    operation_name: Optional[str] = None,
    include_args: bool = False,
    memory_threshold_mb: Optional[float] = None,
    duration_threshold_s: Optional[float] = None
):
    """
    Decorator to monitor performance of functions with memory and duration thresholds
    
    Args:
        operation_name: Name of the operation (defaults to function name)
        include_args: Whether to include function arguments in metrics
        memory_threshold_mb: Optional memory usage threshold in MB
        duration_threshold_s: Optional duration threshold in seconds
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            metadata = {
                'function': func.__name__,
                'module': func.__module__,
                'async': True
            }
            
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
            
            # Record initial memory state
            if HAS_PSUTIL and (memory_threshold_mb is not None):
                try:
                    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    metadata['initial_memory_mb'] = initial_memory
                except Exception as e:
                    logger.warning(f"Failed to get initial memory usage: {e}")
            
            performance_metrics.start_operation(op_name)
            start_time = time.perf_counter()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start_time
                
                # Check duration threshold
                if duration_threshold_s and duration > duration_threshold_s:
                    logger.warning(
                        f"Operation {op_name} exceeded duration threshold: "
                        f"{duration:.2f}s > {duration_threshold_s}s"
                    )
                
                # Check memory threshold
                if HAS_PSUTIL and memory_threshold_mb is not None:
                    try:
                        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
                        memory_increase = final_memory - metadata.get('initial_memory_mb', 0)
                        metadata['memory_increase_mb'] = memory_increase
                        
                        if memory_increase > memory_threshold_mb:
                            logger.warning(
                                f"Operation {op_name} exceeded memory threshold: "
                                f"{memory_increase:.1f}MB > {memory_threshold_mb}MB"
                            )
                            
                            # Trigger garbage collection
                            gc.collect()
                    except Exception as e:
                        logger.warning(f"Failed to check memory threshold: {e}")
                
                performance_metrics.end_operation(op_name, metadata)
                logger.debug(
                    f"{op_name} completed in {duration:.2f}s "
                    f"(Thread: {threading.get_ident()})"
                )
                return result
                
            except Exception as e:
                metadata['error'] = str(e)
                metadata['error_type'] = type(e).__name__
                performance_metrics.end_operation(op_name, metadata)
                logger.error(
                    f"Error in {op_name}: {str(e)}",
                    exc_info=True
                )
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            metadata = {
                'function': func.__name__,
                'module': func.__module__,
                'async': False
            }
            
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
            
            # Record initial memory state
            if HAS_PSUTIL and (memory_threshold_mb is not None):
                try:
                    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    metadata['initial_memory_mb'] = initial_memory
                except Exception as e:
                    logger.warning(f"Failed to get initial memory usage: {e}")
            
            performance_metrics.start_operation(op_name)
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start_time
                
                # Check duration threshold
                if duration_threshold_s and duration > duration_threshold_s:
                    logger.warning(
                        f"Operation {op_name} exceeded duration threshold: "
                        f"{duration:.2f}s > {duration_threshold_s}s"
                    )
                
                # Check memory threshold
                if HAS_PSUTIL and memory_threshold_mb is not None:
                    try:
                        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
                        memory_increase = final_memory - metadata.get('initial_memory_mb', 0)
                        metadata['memory_increase_mb'] = memory_increase
                        
                        if memory_increase > memory_threshold_mb:
                            logger.warning(
                                f"Operation {op_name} exceeded memory threshold: "
                                f"{memory_increase:.1f}MB > {memory_threshold_mb}MB"
                            )
                            
                            # Trigger garbage collection
                            gc.collect()
                    except Exception as e:
                        logger.warning(f"Failed to check memory threshold: {e}")
                
                performance_metrics.end_operation(op_name, metadata)
                logger.debug(
                    f"{op_name} completed in {duration:.2f}s "
                    f"(Thread: {threading.get_ident()})"
                )
                return result
                
            except Exception as e:
                metadata['error'] = str(e)
                metadata['error_type'] = type(e).__name__
                performance_metrics.end_operation(op_name, metadata)
                logger.error(
                    f"Error in {op_name}: {str(e)}",
                    exc_info=True
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def get_system_metrics(include_per_cpu: bool = False) -> Dict[str, Any]:
    """Get comprehensive system metrics"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'pid': os.getpid(),
        'thread_count': threading.active_count(),
        'gc_counts': gc.get_count(),
    }
    
    if HAS_PSUTIL:
        try:
            process = psutil.Process()
            system = {
                'cpu': {
                    'system_percent': psutil.cpu_percent(interval=None),
                    'process_percent': process.cpu_percent(),
                    'count': psutil.cpu_count(),
                    'load_avg': psutil.getloadavg(),
                },
                'memory': {
                    'system': {
                        'total': psutil.virtual_memory().total / 1024 / 1024,  # MB
                        'available': psutil.virtual_memory().available / 1024 / 1024,  # MB
                        'percent': psutil.virtual_memory().percent,
                        'swap_percent': psutil.swap_memory().percent
                    },
                    'process': {
                        'rss': process.memory_info().rss / 1024 / 1024,  # MB
                        'vms': process.memory_info().vms / 1024 / 1024,  # MB
                        'percent': process.memory_percent(),
                        'page_faults': process.memory_info().pfaults if hasattr(process.memory_info(), 'pfaults') else None
                    }
                },
                'disk': {
                    'usage_percent': psutil.disk_usage('/').percent,
                    'io_counters': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None
                },
                'network': {
                    'connections': len(process.connections()),
                    'io_counters': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
                }
            }
            
            if include_per_cpu:
                system['cpu']['per_cpu_percent'] = psutil.cpu_percent(percpu=True)
            
            metrics['system'] = system
            
            # Check for concerning metrics
            if system['memory']['system']['percent'] > MEMORY_WARNING_THRESHOLD:
                logger.warning(
                    f"High system memory usage: {system['memory']['system']['percent']}%"
                )
            if system['cpu']['system_percent'] > CPU_WARNING_THRESHOLD:
                logger.warning(
                    f"High system CPU usage: {system['cpu']['system_percent']}%"
                )
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}", exc_info=True)
    
    return metrics
