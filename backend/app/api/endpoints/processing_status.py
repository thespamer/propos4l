from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import Dict, List, Optional
import asyncio
import json

from app.services.processing_status import get_tracker, active_trackers, cleanup_old_trackers

router = APIRouter()


@router.get("/processing-status/{tracker_id}")
async def get_processing_status(tracker_id: str):
    """Get the current status of a processing task"""
    tracker = get_tracker(tracker_id)
    if not tracker:
        raise HTTPException(status_code=404, detail="Processing task not found")
    
    return tracker.to_dict()


@router.get("/active-processing-tasks")
async def get_active_tasks():
    """Get a list of all active processing tasks"""
    # Clean up old trackers first
    cleanup_old_trackers()
    
    return {
        "tasks": [
            {
                "id": tracker_id,
                "fileName": tracker.file_name,
                "progress": tracker.overall_progress,
                "isComplete": tracker.is_complete
            }
            for tracker_id, tracker in active_trackers.items()
        ]
    }


@router.websocket("/ws/processing-status/{tracker_id}")
async def websocket_processing_status(websocket: WebSocket, tracker_id: str):
    """WebSocket endpoint for real-time processing status updates"""
    await websocket.accept()
    
    tracker = get_tracker(tracker_id)
    if not tracker:
        await websocket.send_text(json.dumps({"error": "Processing task not found"}))
        await websocket.close()
        return
    
    # Create a queue for this connection
    queue = asyncio.Queue()
    
    try:
        # Subscribe to updates
        await tracker.subscribe(queue)
        
        # Send initial state
        await websocket.send_json(tracker.to_dict())
        
        # Listen for updates
        while True:
            # Wait for updates from the tracker
            data = await queue.get()
            
            # Send update to client
            await websocket.send_json(data)
            
            # If processing is complete, close after a delay
            if data.get("isComplete", False):
                await asyncio.sleep(5)  # Keep connection open for 5 more seconds
                break
                
    except WebSocketDisconnect:
        # Client disconnected
        pass
    finally:
        # Unsubscribe from updates
        tracker.unsubscribe(queue)
