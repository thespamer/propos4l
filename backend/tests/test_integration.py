import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.version_control import VersionControl, CommentSystem
from app.services.approval_workflow import ApprovalWorkflow
from app.models.database import Proposal, ProposalVersion, Comment, User

@pytest.fixture
def db_session():
    # This would be your test database session
    pass

@pytest.fixture
def test_users():
    return [
        User(id=1, username="author", email="author@test.com", full_name="Test Author"),
        User(id=2, username="reviewer1", email="rev1@test.com", full_name="Test Reviewer 1"),
        User(id=3, username="reviewer2", email="rev2@test.com", full_name="Test Reviewer 2")
    ]

@pytest.fixture
def test_proposal():
    return Proposal(
        id=1,
        title="Cloud Infrastructure Support Proposal",
        client_name="FinTech Corp",
        industry="Financial Services",
        status="draft",
        metadata={
            "service_type": "Cloud Infrastructure",
            "duration": "6 months",
            "technology": "AWS",
            "team_type": "Hybrid",
            "sla": "99.9%"
        }
    )

class TestProposalWorkflow:
    def test_full_proposal_workflow(self, db_session, test_users, test_proposal):
        version_control = VersionControl()
        comment_system = CommentSystem()
        approval_workflow = ApprovalWorkflow()
        
        author, reviewer1, reviewer2 = test_users
        
        # 1. Create initial version
        initial_content = {
            "title": test_proposal.title,
            "context": "24/7 cloud infrastructure support for financial services",
            "solution": "AWS-based hybrid team solution with 99.9% SLA",
            "scope": "6-month infrastructure management and monitoring",
            "timeline": "Immediate start with 6-month duration",
            "investment": "Based on resource allocation and SLA requirements"
        }
        
        version1 = version_control.create_version(
            session=db_session,
            proposal_id=test_proposal.id,
            content=initial_content,
            user_id=author.id,
            version_notes="Initial draft"
        )
        
        assert version1.version_number == 1
        assert version1.content == initial_content
        
        # 2. Add comments for improvement
        comment1 = comment_system.add_comment(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=reviewer1.id,
            content="Please add more details about the AWS services to be used",
            section="solution"
        )
        
        assert comment1.content == "Please add more details about the AWS services to be used"
        
        # 3. Create revised version based on comments
        revised_content = {
            **initial_content,
            "solution": (
                "AWS-based hybrid team solution with 99.9% SLA, utilizing:\n"
                "- Amazon EC2 for compute resources\n"
                "- Amazon RDS for database management\n"
                "- Amazon CloudWatch for monitoring\n"
                "- AWS Lambda for serverless operations"
            )
        }
        
        version2 = version_control.create_version(
            session=db_session,
            proposal_id=test_proposal.id,
            content=revised_content,
            user_id=author.id,
            version_notes="Added AWS service details"
        )
        
        assert version2.version_number == 2
        
        # 4. Compare versions
        differences = version_control.compare_versions(
            session=db_session,
            proposal_id=test_proposal.id,
            version1=1,
            version2=2
        )
        
        assert "solution" in differences
        assert differences["solution"]["type"] == "modified"
        
        # 5. Submit for review
        review_submission = approval_workflow.submit_for_review(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=author.id,
            reviewers=[reviewer1.id, reviewer2.id]
        )
        
        assert review_submission["status"] == "review"
        assert len(review_submission["metadata"]["reviewers"]) == 2
        
        # 6. First reviewer approves
        review1 = approval_workflow.review_proposal(
            session=db_session,
            proposal_id=test_proposal.id,
            reviewer_id=reviewer1.id,
            approved=True,
            comments="AWS service details look good now"
        )
        
        assert len(review1["metadata"]["approvals"]) == 1
        
        # 7. Check review status
        status = approval_workflow.get_review_status(
            session=db_session,
            proposal_id=test_proposal.id
        )
        
        assert status["status"] == "review"
        assert status["approvals"] == 1
        assert status["pending"] == 1
        
        # 8. Second reviewer approves
        review2 = approval_workflow.review_proposal(
            session=db_session,
            proposal_id=test_proposal.id,
            reviewer_id=reviewer2.id,
            approved=True,
            comments="Timeline and scope are well defined"
        )
        
        assert review2["status"] == "approved"
        assert len(review2["metadata"]["approvals"]) == 2
        
        # 9. Verify final state
        final_status = approval_workflow.get_review_status(
            session=db_session,
            proposal_id=test_proposal.id
        )
        
        assert final_status["status"] == "approved"
        assert final_status["approvals"] == 2
        assert final_status["pending"] == 0
        
        # 10. Verify version history
        history = version_control.get_version_history(
            session=db_session,
            proposal_id=test_proposal.id,
            include_content=True
        )
        
        assert len(history) == 2
        assert history[0]["version_number"] == 2
        assert "AWS Lambda" in history[0]["content"]["solution"]
