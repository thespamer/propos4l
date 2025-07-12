from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.database import get_session
from app.services.processing_status import get_processing_status_service

router = APIRouter()

@router.get("/active-processing-tasks")
async def get_active_processing_tasks(session: Session = Depends(get_session)):
    """
    Retorna todas as tarefas de processamento ativas ou recentemente concluídas
    """
    try:
        # Obter serviço de status de processamento
        status_service = get_processing_status_service()
        
        # Obter todas as tarefas ativas
        active_tasks = status_service.get_all_active_tasks()
        
        # Formatar resposta
        tasks = []
        for task_id, task_info in active_tasks.items():
            tasks.append({
                "id": task_id,
                "fileName": task_info.get("file_name", "Arquivo desconhecido"),
                "progress": task_info.get("progress", 0),
                "isComplete": task_info.get("is_complete", False),
                "startTime": task_info.get("start_time"),
                "lastUpdate": task_info.get("last_update"),
                "currentStep": task_info.get("current_step", ""),
                "steps": task_info.get("steps", [])
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
        status_service = get_processing_status_service()
        success = status_service.remove_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Tarefa {task_id} não encontrada")
        
        return {"message": f"Tarefa {task_id} removida com sucesso"}
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
        status_service = get_processing_status_service()
        active_tasks = status_service.get_all_active_tasks()
        
        total = len(active_tasks)
        completed = sum(1 for task in active_tasks.values() if task.get("is_complete", False))
        in_progress = total - completed
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter resumo de tarefas: {str(e)}")
