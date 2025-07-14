from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.database import get_session
from app.services.processing_status import active_trackers, get_tracker, cleanup_old_trackers

router = APIRouter()

@router.get("/active-processing-tasks")
async def get_active_processing_tasks(session: Session = Depends(get_session)):
    """
    Retorna todas as tarefas de processamento ativas ou recentemente concluídas
    """
    try:
        # Limpar trackers antigos antes de retornar os ativos
        cleanup_old_trackers()
        
        # Formatar resposta
        tasks = []
        for task_id, tracker in active_trackers.items():
            tasks.append({
                "id": task_id,
                "fileName": tracker.file_name,
                "progress": tracker.overall_progress,
                "isComplete": tracker.is_complete,
                "startTime": tracker.start_time.isoformat() if tracker.start_time else None,
                "lastUpdate": tracker.end_time.isoformat() if tracker.end_time else tracker.start_time.isoformat(),
                "currentStep": tracker.get_current_step().name if tracker.get_current_step() else "",
                "steps": [step.to_dict() for step in tracker.steps]
            })
        
        # Ordenar por hora de início (mais recentes primeiro)
        tasks.sort(key=lambda x: x.get("startTime", ""), reverse=True)
        
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter tarefas de processamento: {str(e)}")

@router.delete("/processing-task/{task_id}")
async def delete_processing_task(task_id: str):
    """
    Remove uma tarefa de processamento do histórico
    """
    try:
        if task_id in active_trackers:
            del active_trackers[task_id]
            return {"message": f"Tarefa {task_id} removida com sucesso"}
        else:
            raise HTTPException(status_code=404, detail=f"Tarefa {task_id} não encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover tarefa: {str(e)}")

@router.get("/processing-tasks-summary")
async def get_processing_tasks_summary():
    """
    Retorna um resumo das tarefas de processamento (total, concluídas, em andamento)
    """
    try:
        # Limpar trackers antigos antes de calcular o resumo
        cleanup_old_trackers()
        
        total = len(active_trackers)
        completed = sum(1 for tracker in active_trackers.values() if tracker.is_complete)
        in_progress = total - completed
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter resumo de tarefas: {str(e)}")
