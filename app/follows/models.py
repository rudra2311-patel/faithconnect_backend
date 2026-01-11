from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base


class Follow(Base):
    """
    Follow relationship model.
    
    Represents a worshiper following a leader.
    """
    __tablename__ = "follows"

    id = Column(BigInteger, primary_key=True, index=True)
    worshiper_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    leader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Ensure unique follow relationship
    __table_args__ = (
        UniqueConstraint('worshiper_id', 'leader_id', name='unique_worshiper_leader'),
    )

    def __repr__(self):
        return f"<Follow(worshiper_id={self.worshiper_id}, leader_id={self.leader_id})>"
