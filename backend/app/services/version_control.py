from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import Proposal, ProposalVersion, Comment, User

class VersionControl:
    def __init__(self):
        pass
    
    async def create_version(
        self,
        session: Session,
        proposal_id: int,
        content: Dict,
        user_id: int,
        version_notes: str = ""
    ) -> ProposalVersion:
        """
        Create a new version of a proposal
        """
        # Get the proposal
        proposal = session.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        # Get the latest version number
        latest_version = session.query(ProposalVersion)\
            .filter(ProposalVersion.proposal_id == proposal_id)\
            .order_by(desc(ProposalVersion.version_number))\
            .first()
        
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        # Create new version
        version = ProposalVersion(
            proposal_id=proposal_id,
            content=content,
            version_number=new_version_number,
            created_by=user_id,
            created_at=datetime.utcnow(),
            version_notes=version_notes
        )
        
        session.add(version)
        session.commit()
        return version
    
    async def get_version_history(
        self,
        session: Session,
        proposal_id: int,
        include_content: bool = False
    ) -> List[Dict]:
        """
        Get version history for a proposal
        """
        versions = session.query(ProposalVersion)\
            .filter(ProposalVersion.proposal_id == proposal_id)\
            .order_by(desc(ProposalVersion.version_number))\
            .all()
        
        history = []
        for version in versions:
            version_info = {
                'version_number': version.version_number,
                'created_at': version.created_at,
                'created_by': version.created_by,
                'version_notes': version.version_notes
            }
            if include_content:
                version_info['content'] = version.content
            history.append(version_info)
        
        return history
    
    async def compare_versions(
        self,
        session: Session,
        proposal_id: int,
        version1: int,
        version2: int
    ) -> Dict:
        """
        Compare two versions of a proposal and return differences
        """
        v1 = session.query(ProposalVersion)\
            .filter(
                ProposalVersion.proposal_id == proposal_id,
                ProposalVersion.version_number == version1
            ).first()
        
        v2 = session.query(ProposalVersion)\
            .filter(
                ProposalVersion.proposal_id == proposal_id,
                ProposalVersion.version_number == version2
            ).first()
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        # Compare sections
        differences = {}
        for section in set(v1.content.keys()) | set(v2.content.keys()):
            if section not in v1.content:
                differences[section] = {
                    'type': 'added',
                    'content': v2.content[section]
                }
            elif section not in v2.content:
                differences[section] = {
                    'type': 'removed',
                    'content': v1.content[section]
                }
            elif v1.content[section] != v2.content[section]:
                differences[section] = {
                    'type': 'modified',
                    'old_content': v1.content[section],
                    'new_content': v2.content[section]
                }
        
        return differences

class CommentSystem:
    def __init__(self):
        pass
    
    async def add_comment(
        self,
        session: Session,
        proposal_id: int,
        user_id: int,
        content: str,
        section: Optional[str] = None,
        parent_id: Optional[int] = None
    ) -> Comment:
        """
        Add a comment to a proposal
        """
        comment = Comment(
            proposal_id=proposal_id,
            user_id=user_id,
            content=content,
            section=section,
            parent_id=parent_id,
            created_at=datetime.utcnow()
        )
        
        session.add(comment)
        session.commit()
        return comment
    
    async def get_comments(
        self,
        session: Session,
        proposal_id: int,
        section: Optional[str] = None
    ) -> List[Dict]:
        """
        Get comments for a proposal, optionally filtered by section
        """
        query = session.query(Comment)\
            .filter(Comment.proposal_id == proposal_id)
        
        if section:
            query = query.filter(Comment.section == section)
        
        comments = query.order_by(Comment.created_at).all()
        
        # Organize comments into threads
        comment_threads = []
        comment_map = {}
        
        for comment in comments:
            comment_data = {
                'id': comment.id,
                'content': comment.content,
                'user_id': comment.user_id,
                'created_at': comment.created_at,
                'section': comment.section,
                'replies': []
            }
            
            comment_map[comment.id] = comment_data
            
            if comment.parent_id:
                parent = comment_map.get(comment.parent_id)
                if parent:
                    parent['replies'].append(comment_data)
            else:
                comment_threads.append(comment_data)
        
        return comment_threads
    
    async def update_comment(
        self,
        session: Session,
        comment_id: int,
        user_id: int,
        new_content: str
    ) -> Comment:
        """
        Update a comment
        """
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")
        
        if comment.user_id != user_id:
            raise ValueError("Cannot edit another user's comment")
        
        comment.content = new_content
        comment.updated_at = datetime.utcnow()
        
        session.commit()
        return comment
    
    async def delete_comment(
        self,
        session: Session,
        comment_id: int,
        user_id: int
    ) -> None:
        """
        Delete a comment
        """
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")
        
        if comment.user_id != user_id:
            raise ValueError("Cannot delete another user's comment")
        
        session.delete(comment)
        session.commit()
