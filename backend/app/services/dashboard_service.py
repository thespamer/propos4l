from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import json
import csv
from io import StringIO
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.logging import get_logger
from app.core.monitoring import performance_metrics, get_system_metrics
from app.database import get_session
from sqlmodel import select
from app.models.database import Document, SemanticBlock
import numpy as np

logger = get_logger(__name__)
router = APIRouter()

class DashboardService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self._metrics_history = []
        self._last_update = time.time()
        self.update_interval = 60  # seconds
    
    async def get_performance_metrics(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict:
        """Get aggregated performance metrics"""
        metrics = performance_metrics.get_metrics()
        
        # Filter metrics by time range if specified
        if start_time or end_time:
            filtered_metrics = {}
            for op_name, op_metrics in metrics.items():
                filtered_op_metrics = []
                for metric in op_metrics:
                    metric_time = datetime.fromisoformat(metric['timestamp'])
                    if start_time and metric_time < start_time:
                        continue
                    if end_time and metric_time > end_time:
                        continue
                    filtered_op_metrics.append(metric)
                if filtered_op_metrics:
                    filtered_metrics[op_name] = filtered_op_metrics
            metrics = filtered_metrics
        
        # Aggregate metrics by operation
        aggregated = {}
        for op_name, op_metrics in metrics.items():
            if op_metrics:
                durations = [m['duration'] for m in op_metrics]
                memory = [m['memory_usage'] for m in op_metrics]
                cpu = [m['cpu_percent'] for m in op_metrics]
                
                aggregated[op_name] = {
                    'count': len(op_metrics),
                    'avg_duration': np.mean(durations),
                    'max_duration': max(durations),
                    'min_duration': min(durations),
                    'avg_memory': np.mean(memory),
                    'avg_cpu': np.mean(cpu),
                    'last_execution': op_metrics[-1]['timestamp']
                }
        
        return aggregated
    
    async def get_system_health(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict:
        """Get system health metrics"""
        metrics = get_system_metrics()
        
        # Add historical data
        current_time = time.time()
        if current_time - self._last_update >= self.update_interval:
            self._metrics_history.append({
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            })
            self._last_update = current_time
            
            # Filter by time range if specified
            if start_time or end_time:
                self._metrics_history = [
                    m for m in self._metrics_history
                    if (not start_time or datetime.fromisoformat(m['timestamp']) >= start_time) and
                       (not end_time or datetime.fromisoformat(m['timestamp']) <= end_time)
                ]
            else:
                # Keep last 24 hours of data by default
                cutoff = datetime.now() - timedelta(hours=24)
                self._metrics_history = [
                    m for m in self._metrics_history 
                    if datetime.fromisoformat(m['timestamp']) > cutoff
                ]
        
        return {
            'current': metrics,
            'history': self._metrics_history
        }
    
    async def get_processing_stats(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict:
        """Get document processing statistics"""
        async with get_session() as session:
            # Build query with time filters
            docs_query = select(Document)
            processed_query = select(Document).where(Document.processed == True)
            
            if start_time:
                docs_query = docs_query.where(Document.created_at >= start_time)
                processed_query = processed_query.where(Document.created_at >= start_time)
            if end_time:
                docs_query = docs_query.where(Document.created_at <= end_time)
                processed_query = processed_query.where(Document.created_at <= end_time)
            
            # Get document stats
            total_docs = await session.execute(docs_query)
            total_docs = len(total_docs.scalars().all())
            
            processed_docs = await session.execute(processed_query)
            processed_docs = len(processed_docs.scalars().all())
            
            # Get block stats
            blocks = await session.execute(select(SemanticBlock))
            blocks = blocks.scalars().all()
            
            block_stats = {
                'total': len(blocks),
                'by_type': {},
                'avg_length': np.mean([len(b.content) for b in blocks]) if blocks else 0,
                'confidence_scores': {
                    'high': len([b for b in blocks if b.metadata.get('confidence', 0) >= 0.8]),
                    'medium': len([b for b in blocks if 0.5 <= b.metadata.get('confidence', 0) < 0.8]),
                    'low': len([b for b in blocks if b.metadata.get('confidence', 0) < 0.5])
                }
            }
            
            # Count blocks by type
            for block in blocks:
                block_type = block.block_type.value
                if block_type not in block_stats['by_type']:
                    block_stats['by_type'][block_type] = 0
                block_stats['by_type'][block_type] += 1
        
        return {
            'documents': {
                'total': total_docs,
                'processed': processed_docs,
                'processing_rate': processed_docs / total_docs if total_docs > 0 else 0
            },
            'blocks': block_stats
        }
    
    async def get_nlp_metrics(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict:
        """Get NLP processing metrics"""
        async with get_session() as session:
            blocks = await session.execute(select(SemanticBlock))
            blocks = blocks.scalars().all()
            
            nlp_stats = {
                'entity_types': {},
                'avg_key_phrases': 0,
                'avg_technical_terms': 0,
                'complexity_scores': {
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
            }
            
            for block in blocks:
                # Count entity types
                if 'nlp_analysis' in block.metadata:
                    entities = block.metadata['nlp_analysis'].get('entities', {})
                    for entity_type, entities_list in entities.items():
                        if entity_type not in nlp_stats['entity_types']:
                            nlp_stats['entity_types'][entity_type] = 0
                        nlp_stats['entity_types'][entity_type] += len(entities_list)
                    
                    # Count key phrases and technical terms
                    key_phrases = len(block.metadata['nlp_analysis'].get('key_phrases', []))
                    tech_terms = len(block.metadata['nlp_analysis'].get('technical_terms', []))
                    nlp_stats['avg_key_phrases'] += key_phrases
                    nlp_stats['avg_technical_terms'] += tech_terms
                    
                    # Count complexity scores
                    complexity = block.metadata['nlp_analysis'].get('text_structure', {}).get('complexity_score', 0)
                    if complexity >= 0.7:
                        nlp_stats['complexity_scores']['high'] += 1
                    elif complexity >= 0.4:
                        nlp_stats['complexity_scores']['medium'] += 1
                    else:
                        nlp_stats['complexity_scores']['low'] += 1
            
            # Calculate averages
            total_blocks = len(blocks)
            if total_blocks > 0:
                nlp_stats['avg_key_phrases'] /= total_blocks
                nlp_stats['avg_technical_terms'] /= total_blocks
        
        return nlp_stats

    @staticmethod
    def _convert_to_csv(data: Dict) -> str:
        """Convert dashboard data to CSV format"""
        output = StringIO()
        writer = csv.writer(output)
        
        def flatten_dict(d: Dict, prefix: str = '') -> List[tuple]:
            items = []
            for k, v in d.items():
                new_key = f"{prefix}{k}" if prefix else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, f"{new_key}."))
                else:
                    items.append((new_key, v))
            return items
        
        # Flatten and write data
        flattened = flatten_dict(data)
        writer.writerow(['Metric', 'Value'])
        writer.writerows(flattened)
        
        return output.getvalue()

# API Routes

@router.get("/dashboard/performance/export")
async def export_performance_dashboard(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None)
):
    """Export performance metrics as CSV"""
    try:
        dashboard = DashboardService()
        data = {
            'performance': await dashboard.get_performance_metrics(start_time, end_time),
            'system_health': await dashboard.get_system_health(start_time, end_time)
        }
        
        csv_data = dashboard._convert_to_csv(data)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    except Exception as e:
        logger.error(f"Error exporting performance dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/processing/export")
async def export_processing_dashboard(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None)
):
    """Export processing metrics as CSV"""
    try:
        dashboard = DashboardService()
        data = {
            'processing_stats': await dashboard.get_processing_stats(start_time, end_time),
            'nlp_metrics': await dashboard.get_nlp_metrics(start_time, end_time)
        }
        
        csv_data = dashboard._convert_to_csv(data)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=processing_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    except Exception as e:
        logger.error(f"Error exporting processing dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/performance")
async def get_performance_dashboard(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None)
):
    """Get performance metrics dashboard"""
    try:
        dashboard = DashboardService()
        return {
            'performance': await dashboard.get_performance_metrics(start_time, end_time),
            'system_health': await dashboard.get_system_health(start_time, end_time)
        }
    except Exception as e:
        logger.error(f"Error getting performance dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/processing")
async def get_processing_dashboard(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None)
):
    """Get document processing dashboard"""
    try:
        dashboard = DashboardService()
        return {
            'processing_stats': await dashboard.get_processing_stats(start_time, end_time),
            'nlp_metrics': await dashboard.get_nlp_metrics(start_time, end_time)
        }
    except Exception as e:
        logger.error(f"Error getting processing dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
