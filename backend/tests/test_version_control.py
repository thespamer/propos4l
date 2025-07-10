import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.version_control import VersionControl, CommentSystem
from app.models.database import Proposal, ProposalVersion, Comment, User

@pytest.fixture
def db_session():
    # This would be your test database session
    pass

@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )

@pytest.fixture
def test_proposal():
    return Proposal(
        id=1,
        title="Test Proposal",
        client_name="Test Client",
        industry="Tech",
        status="draft"
    )

class TestVersionControl:
    def test_create_version(self, db_session, test_proposal, test_user):
        vc = VersionControl()
        content = {
            "title": "Test Proposal",
            "context": "Test Context",
            "solution": "Test Solution"
        }
        
        version = vc.create_version(
            session=db_session,
            proposal_id=test_proposal.id,
            content=content,
            user_id=test_user.id,
            version_notes="Initial version"
        )
        
        assert version.proposal_id == test_proposal.id
        assert version.version_number == 1
        assert version.content == content
        assert version.created_by == test_user.id
        assert version.version_notes == "Initial version"

    def test_get_version_history(self, db_session, test_proposal):
        vc = VersionControl()
        history = vc.get_version_history(
            session=db_session,
            proposal_id=test_proposal.id
        )
        
        assert isinstance(history, list)
        if history:
            assert all(
                isinstance(v["version_number"], int) and
                isinstance(v["created_at"], datetime)
                for v in history
            )

    def test_compare_versions(self, db_session, test_proposal):
        vc = VersionControl()
        differences = vc.compare_versions(
            session=db_session,
            proposal_id=test_proposal.id,
            version1=1,
            version2=2
        )
        
        assert isinstance(differences, dict)

class TestCommentSystem:
    def test_add_comment(self, db_session, test_proposal, test_user):
        cs = CommentSystem()
        comment = cs.add_comment(
            session=db_session,
            proposal_id=test_proposal.id,
            user_id=test_user.id,
            content="Test comment",
            section="context"
        )
        
        assert comment.proposal_id == test_proposal.id
        assert comment.user_id == test_user.id
        assert comment.content == "Test comment"
        assert comment.section == "context"

    def test_get_comments(self, db_session, test_proposal):
        cs = CommentSystem()
        comments = cs.get_comments(
            session=db_session,
            proposal_id=test_proposal.id
        )
        
        assert isinstance(comments, list)
        if comments:
            assert all(isinstance(c["id"], int) for c in comments)

    def test_update_comment(self, db_session, test_user):
        cs = CommentSystem()
        comment = Comment(id=1, user_id=test_user.id, content="Original")
        
        updated = cs.update_comment(
            session=db_session,
            comment_id=comment.id,
            user_id=test_user.id,
            new_content="Updated content"
        )
        
        assert updated.content == "Updated content"

    def test_delete_comment(self, db_session, test_user):
        cs = CommentSystem()
        comment = Comment(id=1, user_id=test_user.id)
        
        cs.delete_comment(
            session=db_session,
            comment_id=comment.id,
            user_id=test_user.id
        )
        # Should not raise any exceptions
