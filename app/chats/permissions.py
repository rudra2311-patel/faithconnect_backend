"""
Permission checks for chat operations.

Ensures business rules are enforced:
- Worshipers must follow leaders to initiate chats
- Only chat participants can access conversations
"""

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.follows.models import Follow
from app.chats.models import Chat


def verify_follow_exists(
    db: Session,
    worshiper_id: int,
    leader_id: int
) -> None:
    """
    Verify that worshiper follows the leader before allowing chat.
    
    Business rule: Private messaging is only meaningful in an existing
    worshiper-leader relationship. If someone doesn't follow you,
    they shouldn't be able to message you privately.
    
    Raises:
        HTTPException 403: If worshiper doesn't follow leader
    """
    # Check if follow relationship exists
    query = select(Follow).where(
        and_(
            Follow.worshiper_id == worshiper_id,
            Follow.leader_id == leader_id
        )
    )
    result = db.execute(query)
    follow = result.scalar_one_or_none()
    
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must follow this leader to send messages"
        )


def verify_chat_participant(
    db: Session,
    chat_id: int,
    user_id: int
) -> Chat:
    """
    Verify that user is a participant in the chat.
    
    Business rule: Only the worshiper and leader involved in a chat
    can access its messages. This ensures privacy.
    
    Returns:
        Chat: The chat object if user is a participant
        
    Raises:
        HTTPException 404: If chat doesn't exist
        HTTPException 403: If user is not a participant
    """
    # Get the chat
    query = select(Chat).where(Chat.id == chat_id)
    result = db.execute(query)
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Check if user is a participant
    if user_id not in [chat.worshiper_id, chat.leader_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access chats you are a participant in"
        )
    
    return chat


def verify_chat_by_leader(
    db: Session,
    worshiper_id: int,
    leader_id: int,
    user_id: int
) -> Chat:
    """
    Verify that user is a participant in the chat between worshiper and leader.
    
    Used for GET /chats/{leader_id} endpoint where we identify chat by leader_id.
    
    Returns:
        Chat: The chat object if user is a participant
        
    Raises:
        HTTPException 404: If chat doesn't exist
        HTTPException 403: If user is not a participant
    """
    # Get the chat by participants
    query = select(Chat).where(
        and_(
            Chat.worshiper_id == worshiper_id,
            Chat.leader_id == leader_id
        )
    )
    result = db.execute(query)
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Check if user is a participant
    if user_id not in [chat.worshiper_id, chat.leader_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access chats you are a participant in"
        )
    
    return chat
