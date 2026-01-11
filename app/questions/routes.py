"""
Routes for worshiper-leader question system.

Enables private Q&A between worshipers and their spiritual leaders.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User, UserRole
from app.questions.schemas import (
    AskQuestionRequest,
    AnswerQuestionRequest,
    QuestionResponse,
    LeaderQuestionsResponse
)
from app.questions.services import ask_question, get_leader_questions, answer_question
from app.questions.permissions import verify_worshiper_follows_leader, verify_leader_owns_question


router = APIRouter(tags=["Questions"])


@router.post(
    "/leaders/{leader_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_question_to_leader(
    leader_id: int,
    question_data: AskQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Worshiper asks a question to a leader they follow.
    
    Role Enforcement: WORSHIPERS ONLY (HTTP 403 for leaders).
    Follow Requirement: Must follow the leader (HTTP 403 if not following).
    
    Real-world use case:
    A worshiper sees a leader's posts and wants personal guidance.
    They can submit a private question which goes into the leader's
    inbox for thoughtful response.
    
    This enables deeper 1:1 spiritual guidance beyond public content.
    
    Workflow:
    1. Worshiper follows a leader
    2. Worshiper has a personal question
    3. Submits question via this endpoint
    4. Question appears in leader's inbox (GET /leaders/questions)
    5. Leader responds when ready (POST /leaders/questions/{id}/answer)
    6. Worshiper sees answer (future endpoint: GET /worshipers/me/questions)
    """
    # Role enforcement: only worshipers can ask questions
    if current_user.role != UserRole.WORSHIPER:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only worshipers can ask questions to leaders"
        )
    
    # Verify worshiper follows this leader
    verify_worshiper_follows_leader(
        db=db,
        worshiper_id=current_user.id,
        leader_id=leader_id
    )
    
    # Create the question
    question = ask_question(
        db=db,
        worshiper_id=current_user.id,
        leader_id=leader_id,
        question_data=question_data
    )
    
    return question


@router.get("/leaders/questions", response_model=LeaderQuestionsResponse)
def get_my_questions_inbox(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Leader views their question inbox.
    
    Role Enforcement: LEADERS ONLY (HTTP 403 for worshipers).
    
    Real-world use case:
    Leader opens their inbox to see which worshipers need guidance.
    Questions are organized by status to help prioritize responses.
    
    Returns:
    - pending: Questions waiting for answer (prioritize these)
    - answered: Questions already responded to (history/archive)
    
    Each question includes:
    - Worshiper's name (context about who asked)
    - Question text
    - When it was asked
    - Answer (if provided)
    - When it was answered (if applicable)
    
    UX: Two-tab interface - "Pending" and "Answered"
    """
    # Role enforcement: only leaders can view question inbox
    if current_user.role != UserRole.LEADER:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can access question inbox"
        )
    
    # Get all questions for this leader
    questions = get_leader_questions(db=db, leader_id=current_user.id)
    
    return LeaderQuestionsResponse(
        pending=questions["pending"],
        answered=questions["answered"],
        total_pending=len(questions["pending"]),
        total_answered=len(questions["answered"])
    )


@router.post(
    "/leaders/questions/{question_id}/answer",
    response_model=QuestionResponse
)
def answer_worshiper_question(
    question_id: int,
    answer_data: AnswerQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Leader answers a question from their inbox.
    
    Role Enforcement: LEADERS ONLY (HTTP 403 for worshipers).
    Ownership Check: Can only answer questions addressed to you (HTTP 403).
    
    Real-world use case:
    Leader has reflected on a worshiper's question and is ready
    to provide thoughtful spiritual guidance. The answer is saved
    and the worshiper can see the response.
    
    Once answered:
    - answered = true
    - answered_at = current timestamp
    - Question moves from "pending" to "answered" in inbox
    
    This is asynchronous by design - leaders can take time to
    craft meaningful responses rather than rushing quick replies.
    """
    # Role enforcement: only leaders can answer questions
    if current_user.role != UserRole.LEADER:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can answer questions"
        )
    
    # Verify leader owns this question
    question = verify_leader_owns_question(
        db=db,
        leader_id=current_user.id,
        question_id=question_id
    )
    
    # Answer the question
    answered_question = answer_question(
        db=db,
        question=question,
        answer_data=answer_data
    )
    
    return answered_question
