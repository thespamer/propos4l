from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.models.database import Proposal, ProposalVersion, Comment, User
from app.services.version_control import VersionControl, CommentSystem
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/version-control", tags=["version-control"])
version_control = VersionControl()
comment_system = CommentSystem()

@router.post("/versions/{proposal_id}", response_model=ProposalVersion)
async def create_version(
    proposal_id: int,
    content: dict,
    version_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new version of a proposal"""
    try:
        version = await version_control.create_version(
            session=db,
            proposal_id=proposal_id,
            content=content,
            user_id=current_user.id,
            version_notes=version_notes
        )
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/versions/{proposal_id}", response_model=List[dict])
async def get_version_history(
    proposal_id: int,
    include_content: bool = False,
    db: Session = Depends(get_db)
):
    """Get version history for a proposal"""
    try:
        history = await version_control.get_version_history(
            session=db,
            proposal_id=proposal_id,
            include_content=include_content
        )
        return history
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/versions/compare/{proposal_id}")
async def compare_versions(
    proposal_id: int,
    version1: int,
    version2: int,
    db: Session = Depends(get_db)
):
    """Compare two versions of a proposal"""
    try:
        differences = await version_control.compare_versions(
            session=db,
            proposal_id=proposal_id,
            version1=version1,
            version2=version2
        )
        return differences
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/comments/{proposal_id}", response_model=Comment)
async def add_comment(
    proposal_id: int,
    content: str,
    section: Optional[str] = None,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a comment to a proposal"""
    try:
        comment = await comment_system.add_comment(
            session=db,
            proposal_id=proposal_id,
            user_id=current_user.id,
            content=content,
            section=section,
            parent_id=parent_id
        )
        return comment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/comments/{proposal_id}", response_model=List[dict])
async def get_comments(
    proposal_id: int,
    section: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get comments for a proposal"""
    try:
        comments = await comment_system.get_comments(
            session=db,
            proposal_id=proposal_id,
            section=section
        )
        return comments
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/comments/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: int,
    new_content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a comment"""
    try:
        comment = await comment_system.update_comment(
            session=db,
            comment_id=comment_id,
            user_id=current_user.id,
            new_content=new_content
        )
        return comment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment"""
    try:
        await comment_system.delete_comment(
            session=db,
            comment_id=comment_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
