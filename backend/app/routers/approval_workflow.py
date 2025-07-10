from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.models.database import User
from app.services.approval_workflow import ApprovalWorkflow
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/approval", tags=["approval"])
workflow = ApprovalWorkflow()

@router.post("/{proposal_id}/submit", response_model=Dict)
async def submit_for_review(
    proposal_id: int,
    reviewers: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a proposal for review"""
    try:
        result = await workflow.submit_for_review(
            session=db,
            proposal_id=proposal_id,
            user_id=current_user.id,
            reviewers=reviewers
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{proposal_id}/review", response_model=Dict)
async def review_proposal(
    proposal_id: int,
    approved: bool,
    comments: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Review a proposal (approve or reject)"""
    try:
        result = await workflow.review_proposal(
            session=db,
            proposal_id=proposal_id,
            reviewer_id=current_user.id,
            approved=approved,
            comments=comments
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{proposal_id}/status", response_model=Dict)
async def get_review_status(
    proposal_id: int,
    db: Session = Depends(get_db)
):
    """Get the current review status of a proposal"""
    try:
        status = await workflow.get_review_status(
            session=db,
            proposal_id=proposal_id
        )
        return status
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{proposal_id}/cancel", response_model=Dict)
async def cancel_review(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an ongoing review"""
    try:
        result = await workflow.cancel_review(
            session=db,
            proposal_id=proposal_id,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
