"""
Business logic for question operations.

Handles question creation, retrieval, and answering.
"""

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.questions.models import Question
from app.questions.schemas import AskQuestionRequest, AnswerQuestionRequest


def ask_question(
    db: Session,
    worshiper_id: int,
    leader_id: int,
    question_data: AskQuestionRequest
) -> Question:
    """
    Create a new question from worshiper to leader.
    
    Real-world use case:
    A worshiper is struggling with doubt and wants personal guidance
    from their spiritual leader. They submit a question privately,
    which goes into the leader's inbox for thoughtful response.
    
    Returns:
        Question: The newly created question (answered = False)
    """
    # Create new question
    question = Question(
        worshiper_id=worshiper_id,
        leader_id=leader_id,
        question_text=question_data.question_text,
        answered=False,
        answer_text=None,
        answered_at=None
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return question


def get_leader_questions(
    db: Session,
    leader_id: int
) -> dict:
    """
    Get all questions for a leader, organized by status.
    
    Real-world use case:
    Leader opens their inbox to see which worshipers need guidance.
    Pending questions are prioritized (need attention).
    Answered questions provide history/context.
    
    Returns:
        dict: {
            "pending": [questions where answered = False],
            "answered": [questions where answered = True]
        }
    """
    # Get all questions for this leader with worshiper info
    query = select(Question).where(
        Question.leader_id == leader_id
    ).options(
        joinedload(Question.worshiper)  # Eager load worshiper data
    ).order_by(
        Question.created_at.desc()  # Newest first
    )
    
    result = db.execute(query)
    all_questions = result.scalars().all()
    
    # Separate by status
    pending = [q for q in all_questions if not q.answered]
    answered = [q for q in all_questions if q.answered]
    
    return {
        "pending": pending,
        "answered": answered
    }


def answer_question(
    db: Session,
    question: Question,
    answer_data: AnswerQuestionRequest
) -> Question:
    """
    Leader answers a question.
    
    Real-world use case:
    Leader has reflected on the worshiper's question and is ready
    to provide spiritual guidance. The answer is saved and the
    worshiper can now see the response.
    
    Args:
        question: The Question object (already verified via permissions)
        answer_data: The answer text
        
    Returns:
        Question: Updated question with answer
    """
    # Update question with answer
    question.answer_text = answer_data.answer_text
    question.answered = True
    question.answered_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(question)
    
    # UX: Notify worshiper that their question was answered
    # This provides closure and encourages continued engagement
    from app.notifications.services import create_notification
    from app.auth.models import User
    
    # Get leader info for notification message
    leader = db.query(User).filter(User.id == question.leader_id).first()
    
    create_notification(
        db=db,
        user_id=question.worshiper_id,
        type="question_answered",
        message=f"{leader.name} answered your question",
        reference_type="question",
        reference_id=question.id
    )
    
    return question
