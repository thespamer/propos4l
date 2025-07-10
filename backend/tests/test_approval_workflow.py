import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.approval_workflow import ApprovalWorkflow
from app.models.database import Proposal, User

@pytest.fixture
def db_session():
    # This would be your test database session
    pass

@pytest.fixture
def test_proposal():
    return Proposal(
        id=1,
        title="Test Proposal",
        client_name="Test Client",
        industry="Tech",
        status="draft",
        metadata={}
    )

@pytest.fixture
def test_users():
    return [
        User(id=1, username="submitter", email="sub@test.com", full_name="Test Submitter"),
        User(id=2, username="reviewer1", email="rev1@test.com", full_name="Test Reviewer 1"),
        User(id=3, username="reviewer2", email="rev2@test.com", full_name="Test Reviewer 2")
    ]

class TestApprovalWorkflow:
    def test_submit_for_review(self, db_session, test_proposal, test_users):
        workflow = ApprovalWorkflow()
        result = workflow.submit_for_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_users[0].id,
            reviewers=[test_users[1].id, test_users[2].id]
        )
        
        assert result["status"] == "review"
        assert len(result["metadata"]["reviewers"]) == 2
        assert result["metadata"]["review_submitted_by"] == test_users[0].id
        assert "review_submitted_at" in result["metadata"]

    def test_review_proposal_approve(self, db_session, test_proposal, test_users):
        workflow = ApprovalWorkflow()
        
        # First submit for review
        workflow.submit_for_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_users[0].id,
            reviewers=[test_users[1].id]
        )
        
        # Then approve
        result = workflow.review_proposal(
            session=db_session,
            proposal_id=test_proposal.id,
            reviewer_id=test_users[1].id,
            approved=True,
            comments="Looks good!"
        )
        
        assert result["status"] == "approved"
        assert len(result["metadata"]["approvals"]) == 1
        assert len(result["metadata"]["rejections"]) == 0

    def test_review_proposal_reject(self, db_session, test_proposal, test_users):
        workflow = ApprovalWorkflow()
        
        # First submit for review
        workflow.submit_for_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_users[0].id,
            reviewers=[test_users[1].id]
        )
        
        # Then reject
        result = workflow.review_proposal(
            session=db_session,
            proposal_id=test_proposal.id,
            reviewer_id=test_users[1].id,
            approved=False,
            comments="Needs revision"
        )
        
        assert result["status"] == "draft"
        assert len(result["metadata"]["rejections"]) == 1
        assert "Needs revision" in result["metadata"]["review_comments"][0]

    def test_get_review_status(self, db_session, test_proposal, test_users):
        workflow = ApprovalWorkflow()
        
        # Submit for review
        workflow.submit_for_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_users[0].id,
            reviewers=[test_users[1].id, test_users[2].id]
        )
        
        # Get status
        status = workflow.get_review_status(
            session=db_session,
            proposal_id=test_proposal.id
        )
        
        assert status["status"] == "review"
        assert status["pending"] == 2
        assert status["approvals"] == 0
        assert status["rejections"] == 0

    def test_cancel_review(self, db_session, test_proposal, test_users):
        workflow = ApprovalWorkflow()
        
        # Submit for review
        workflow.submit_for_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_users[0].id,
            reviewers=[test_users[1].id]
        )
        
        # Cancel review
        result = workflow.cancel_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_users[0].id
        )
        
        assert result["status"] == "draft"
        assert "reviewers" not in result
        assert "approvals" not in result
        assert "rejections" not in result

    def test_multiple_reviewers_approval(self, db_session, test_proposal, test_users):
        workflow = ApprovalWorkflow()
        
        # Submit for review
        workflow.submit_for_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_users[0].id,
            reviewers=[test_users[1].id, test_users[2].id]
        )
        
        # First reviewer approves
        workflow.review_proposal(
            session=db_session,
            proposal_id=test_proposal.id,
            reviewer_id=test_users[1].id,
            approved=True,
            comments="Approved by reviewer 1"
        )
        
        status = workflow.get_review_status(
            session=db_session,
            proposal_id=test_proposal.id
        )
        assert status["status"] == "review"
        assert status["approvals"] == 1
        assert status["pending"] == 1
        
        # Second reviewer approves
        result = workflow.review_proposal(
            session=db_session,
            proposal_id=test_proposal.id,
            reviewer_id=test_users[2].id,
            approved=True,
            comments="Approved by reviewer 2"
        )
        
        assert result["status"] == "approved"
        assert len(result["metadata"]["approvals"]) == 2
        assert result["metadata"]["approvals"][0]["comments"] == "Approved by reviewer 1"
        assert result["metadata"]["approvals"][1]["comments"] == "Approved by reviewer 2"
