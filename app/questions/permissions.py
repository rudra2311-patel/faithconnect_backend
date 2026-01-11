"""
Permission checks for question operations.

Ensures business rules are enforced:
- Only worshipers who follow a leader can ask questions
- Only leaders who own a question can answer it
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.follows.models import Follow
from app.questions.models import Question


def verify_worshiper_follows_leader(
    db: Session,
    worshiper_id: int,
    leader_id: int
) -> None:
    """
    Verify that worshiper follows the leader before allowing question.
    
    Business rule: Questions are only meaningful in an existing
    worshiper-leader relationship. If someone doesn't follow you,
    they shouldn't be able to ask you questions.
    
    Raises:
        HTTPException 403: If worshiper doesn't follow leader
    """
    # Check if follow relationship exists
    query = select(Follow).where(
        Follow.worshiper_id == worshiper_id,
        Follow.leader_id == leader_id
    )
    result = db.execute(query)
    follow = result.scalar_one_or_none()
    
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must follow this leader to ask questions"
        )


def verify_leader_owns_question(
    db: Session,
    leader_id: int,
    question_id: int
) -> Question:
    """
    Verify that the leader owns the question before allowing answer.
    
    Business rule: Leaders can only answer questions that were
    addressed to them, not questions meant for other leaders.
    
    Returns:
        Question: The question object if owned by leader
        
    Raises:
        HTTPException 404: If question doesn't exist
        HTTPException 403: If question is not for this leader
    """
    # Get the question
    query = select(Question).where(Question.id == question_id)
    result = db.execute(query)
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    if question.leader_id != leader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only answer questions addressed to you"
        )
    
    return question
