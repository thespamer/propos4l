from typing import Dict, List, Optional, Any
from typing import Dict, List, Optional, Any
import asyncio
import uuid
from datetime import datetime

class ProcessingStatus:
    WAITING = "waiting"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    
    @classmethod
    def values(cls) -> List[str]:
        """Retorna todos os valores possíveis"""
        return [value for key, value in cls.__dict__.items() 
                if not key.startswith('_') and isinstance(value, str)]


class ProcessingStep:
    def __init__(
        self,
        step_id: str,
        name: str,
        description: str,
        percentage_of_total: float,
    ):
        self.id = step_id
        self.name = name
        self.description = description
        self.percentage_of_total = percentage_of_total
        self.status = ProcessingStatus.WAITING
        self.details = None
        self.start_time = None
        self.end_time = None
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "percentageOfTotal": self.percentage_of_total,
            "status": self.status,
            "details": self.details,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "error": str(self.error) if self.error else None,
        }

    def start(self, details: Optional[str] = None) -> None:
        self.status = ProcessingStatus.PROCESSING
        self.start_time = datetime.now()
        if details:
            self.details = details

    def complete(self, details: Optional[str] = None) -> None:
        self.status = ProcessingStatus.SUCCESS
        self.end_time = datetime.now()
        if details:
            self.details = details

    def fail(self, error: Exception, details: Optional[str] = None) -> None:
        self.status = ProcessingStatus.ERROR
        self.end_time = datetime.now()
        self.error = error
        if details:
            self.details = details

    def skip(self, reason: Optional[str] = None) -> None:
        self.status = ProcessingStatus.SKIPPED
        self.end_time = datetime.now()
        if reason:
            self.details = reason


class ProcessingTracker:
    def __init__(self, file_name: str):
        self.id = str(uuid.uuid4())
        self.file_name = file_name
        self.steps: List[ProcessingStep] = []
        self.current_step_index = -1
        self.overall_progress = 0
        self.start_time = datetime.now()
        self.end_time = None
        self.is_complete = False
        self.subscribers = set()

    def add_step(
        self, name: str, description: str, percentage_of_total: float
    ) -> ProcessingStep:
        step_id = f"step_{len(self.steps)}"
        step = ProcessingStep(step_id, name, description, percentage_of_total)
        self.steps.append(step)
        return step

    def get_current_step(self) -> Optional[ProcessingStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    async def start_next_step(self, details: Optional[str] = None) -> Optional[ProcessingStep]:
        self.current_step_index += 1
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            step.start(details)
            self._update_progress()
            await self._notify_subscribers()
            return step
        return None

    async def complete_current_step(self, details: Optional[str] = None) -> None:
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            step.complete(details)
            self._update_progress()
            await self._notify_subscribers()

    async def fail_current_step(self, error: Exception, details: Optional[str] = None) -> None:
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            step.fail(error, details)
            self._update_progress()
            await self._notify_subscribers()

    async def skip_current_step(self, reason: Optional[str] = None) -> None:
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            step.skip(reason)
            self._update_progress()
            await self._notify_subscribers()

    async def complete_processing(self) -> None:
        self.is_complete = True
        self.end_time = datetime.now()
        self.overall_progress = 100
        await self._notify_subscribers()

    def _update_progress(self) -> None:
        completed_percentage = 0
        for i, step in enumerate(self.steps):
            if i < self.current_step_index:
                # Previous steps are fully counted
                completed_percentage += step.percentage_of_total
            elif i == self.current_step_index:
                # Current step is counted based on status
                if step.status == ProcessingStatus.SUCCESS:
                    completed_percentage += step.percentage_of_total
                elif step.status == ProcessingStatus.PROCESSING:
                    # Assume halfway through for simplicity
                    completed_percentage += step.percentage_of_total * 0.5
                elif step.status == ProcessingStatus.SKIPPED:
                    completed_percentage += step.percentage_of_total
            # Future steps are not counted

        self.overall_progress = min(round(completed_percentage, 1), 100)

    def to_dict(self) -> Dict[str, Any]:
        current_step = self.get_current_step()
        return {
            "id": self.id,
            "fileName": self.file_name,
            "steps": [step.to_dict() for step in self.steps],
            "currentStepId": current_step.id if current_step else None,
            "overallProgress": self.overall_progress,
            "startTime": self.start_time.isoformat(),
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "isComplete": self.is_complete,
        }

    async def subscribe(self, queue: asyncio.Queue) -> None:
        self.subscribers.add(queue)
        # Send initial state
        await queue.put(self.to_dict())

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    async def _notify_subscribers(self) -> None:
        data = self.to_dict()
        for queue in self.subscribers:
            await queue.put(data)


# Global registry of active processing trackers
active_trackers: Dict[str, ProcessingTracker] = {}


def create_pdf_processing_tracker(file_name: str) -> ProcessingTracker:
    """Create a standard PDF processing tracker with predefined steps"""
    tracker = ProcessingTracker(file_name)
    
    # Define standard PDF processing steps with their relative weights
    tracker.add_step(
        "Extração de Texto", 
        "Extraindo texto e metadados do PDF", 
        25.0
    )
    tracker.add_step(
        "Identificação de Seções", 
        "Analisando e classificando seções do documento", 
        20.0
    )
    tracker.add_step(
        "Extração de Informações-chave", 
        "Identificando entidades, palavras-chave e resumos", 
        20.0
    )
    tracker.add_step(
        "Indexação Vetorial", 
        "Convertendo texto em vetores para busca semântica", 
        15.0
    )
    tracker.add_step(
        "Armazenamento", 
        "Salvando metadados e organizando informações", 
        10.0
    )
    tracker.add_step(
        "Finalização", 
        "Concluindo processamento e disponibilizando documento", 
        10.0
    )
    
    # Register the tracker
    active_trackers[tracker.id] = tracker
    
    return tracker


def get_tracker(tracker_id: str) -> Optional[ProcessingTracker]:
    """Get a processing tracker by ID"""
    return active_trackers.get(tracker_id)


def cleanup_old_trackers() -> None:
    """Remove completed trackers older than 1 hour"""
    now = datetime.now()
    to_remove = []
    
    for tracker_id, tracker in active_trackers.items():
        if tracker.is_complete and tracker.end_time:
            # If completed more than 1 hour ago
            time_diff = (now - tracker.end_time).total_seconds()
            if time_diff > 3600:  # 1 hour in seconds
                to_remove.append(tracker_id)
    
    for tracker_id in to_remove:
        del active_trackers[tracker_id]
