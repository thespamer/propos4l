from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import Proposal, User

class ApprovalWorkflow:
    def __init__(self):
        pass
    
    async def submit_for_review(
        self,
        session: Session,
        proposal_id: int,
        user_id: int,
        reviewers: List[int]
    ) -> Dict:
        """
        Submit a proposal for review
        """
        proposal = session.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if proposal.status != "draft":
            raise ValueError("Only draft proposals can be submitted for review")
        
        # Update proposal status and metadata
        proposal.status = "review"
        proposal.metadata.update({
            "review_submitted_by": user_id,
            "review_submitted_at": datetime.utcnow().isoformat(),
            "reviewers": reviewers,
            "approvals": [],
            "rejections": [],
            "review_comments": []
        })
        
        session.commit()
        return {
            "status": "review",
            "metadata": proposal.metadata
        }
    
    async def review_proposal(
        self,
        session: Session,
        proposal_id: int,
        reviewer_id: int,
        approved: bool,
        comments: str = ""
    ) -> Dict:
        """
        Review a proposal (approve or reject)
        """
        proposal = session.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if proposal.status != "review":
            raise ValueError("Proposal is not in review status")
        
        if reviewer_id not in proposal.metadata.get("reviewers", []):
            raise ValueError("User is not authorized to review this proposal")
        
        # Add review decision
        review = {
            "reviewer_id": reviewer_id,
            "decision": "approved" if approved else "rejected",
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if approved:
            proposal.metadata["approvals"].append(review)
        else:
            proposal.metadata["rejections"].append(review)
        
        # Check if all reviewers have responded
        total_responses = len(proposal.metadata["approvals"]) + len(proposal.metadata["rejections"])
        if total_responses == len(proposal.metadata["reviewers"]):
            # If all approved, mark as approved
            if len(proposal.metadata["rejections"]) == 0:
                proposal.status = "approved"
            # If any rejections, mark as draft and clear review data
            else:
                proposal.status = "draft"
                proposal.metadata["review_comments"].extend([
                    f"Rejected by {r['reviewer_id']}: {r['comments']}"
                    for r in proposal.metadata["rejections"]
                ])
                proposal.metadata.pop("reviewers", None)
                proposal.metadata.pop("approvals", None)
                proposal.metadata.pop("rejections", None)
        
        session.commit()
        return {
            "status": proposal.status,
            "metadata": proposal.metadata
        }
    
    async def get_review_status(
        self,
        session: Session,
        proposal_id: int
    ) -> Dict:
        """
        Get the current review status of a proposal
        """
        proposal = session.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if proposal.status not in ["review", "approved"]:
            return {
                "status": proposal.status,
                "message": "Proposal is not under review"
            }
        
        return {
            "status": proposal.status,
            "metadata": proposal.metadata,
            "approvals": len(proposal.metadata.get("approvals", [])),
            "rejections": len(proposal.metadata.get("rejections", [])),
            "pending": len(proposal.metadata.get("reviewers", [])) - 
                      (len(proposal.metadata.get("approvals", [])) + 
                       len(proposal.metadata.get("rejections", [])))
        }
    
    async def cancel_review(
        self,
        session: Session,
        proposal_id: int,
        user_id: int
    ) -> Dict:
        """
        Cancel an ongoing review
        """
        proposal = session.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        if proposal.status != "review":
            raise ValueError("Proposal is not under review")
        
        if proposal.metadata.get("review_submitted_by") != user_id:
            raise ValueError("Only the submitter can cancel the review")
        
        proposal.status = "draft"
        proposal.metadata.pop("reviewers", None)
        proposal.metadata.pop("approvals", None)
        proposal.metadata.pop("rejections", None)
        proposal.metadata.pop("review_submitted_by", None)
        proposal.metadata.pop("review_submitted_at", None)
        
        session.commit()
        return {
            "status": "draft",
            "message": "Review cancelled successfully"
        }
