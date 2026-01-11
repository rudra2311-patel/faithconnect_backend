"""
Business logic for chat operations.

Handles chat creation, message sending, and chat retrieval.
"""

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.chats.models import Chat, Message, SenderRole
from app.chats.schemas import SendMessageRequest
from app.auth.models import UserRole


def get_or_create_chat(
    db: Session,
    worshiper_id: int,
    leader_id: int
) -> Chat:
    """
    Get existing chat or create new one for worshiper-leader pair.
    
    Real-world use case:
    When a worshiper first messages a leader, a chat is created automatically.
    Subsequent messages use the same chat. This keeps conversations organized.
    
    Returns:
        Chat: Existing or newly created chat
    """
    # Try to find existing chat
    query = select(Chat).where(
        and_(
            Chat.worshiper_id == worshiper_id,
            Chat.leader_id == leader_id
        )
    )
    result = db.execute(query)
    chat = result.scalar_one_or_none()
    
    if chat:
        return chat
    
    # Create new chat
    chat = Chat(
        worshiper_id=worshiper_id,
        leader_id=leader_id
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    return chat


def send_message(
    db: Session,
    chat: Chat,
    sender_id: int,
    sender_role: UserRole,
    message_data: SendMessageRequest
) -> Message:
    """
    Send a message in a chat.
    
    Real-world use case:
    User (worshiper or leader) sends a message seeking or providing
    spiritual guidance. Messages are immutable once sent to maintain
    authentic conversation history.
    
    Returns:
        Message: The newly created message
    """
    # Map UserRole to SenderRole
    sender_role_value = SenderRole.WORSHIPER if sender_role == UserRole.WORSHIPER else SenderRole.LEADER
    
    # Create message
    message = Message(
        chat_id=chat.id,
        sender_id=sender_id,
        sender_role=sender_role_value,
        content_text=message_data.content_text
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # UX: Notify the other participant about new message
    # This keeps conversations flowing for spiritual guidance
    from app.notifications.services import create_notification
    from app.auth.models import User
    
    # Get sender info for notification message
    sender = db.query(User).filter(User.id == sender_id).first()
    
    # Determine recipient (the other participant in chat)
    recipient_id = chat.leader_id if sender_id == chat.worshiper_id else chat.worshiper_id
    
    create_notification(
        db=db,
        user_id=recipient_id,
        type="new_message",
        message=f"{sender.name} sent you a message",
        reference_type="chat",
        reference_id=chat.id
    )
    
    return message


def get_chat_with_messages(
    db: Session,
    worshiper_id: int,
    leader_id: int
) -> Optional[Chat]:
    """
    Get a chat with all messages and participant info.
    
    Real-world use case:
    User opens a conversation to see message history and continue
    the spiritual dialogue.
    
    Returns:
        Chat: Chat with messages and participant info, or None if not found
    """
    # Get chat with all relationships loaded
    query = select(Chat).where(
        and_(
            Chat.worshiper_id == worshiper_id,
            Chat.leader_id == leader_id
        )
    ).options(
        joinedload(Chat.worshiper),
        joinedload(Chat.leader),
        joinedload(Chat.messages).joinedload(Message.sender)
    )
    
    result = db.execute(query)
    chat = result.scalar_one_or_none()
    
    return chat


def get_leader_chats(
    db: Session,
    leader_id: int
) -> list[Chat]:
    """
    Get all chats for a leader (inbox view).
    
    Real-world use case:
    Leader opens their inbox to see all worshipers who have messaged them.
    Chats are ordered by most recent message to prioritize active conversations.
    
    Returns:
        list[Chat]: Chats with participant info and messages
    """
    # Get all chats where user is the leader
    query = select(Chat).where(
        Chat.leader_id == leader_id
    ).options(
        joinedload(Chat.worshiper),
        joinedload(Chat.leader),
        joinedload(Chat.messages).joinedload(Message.sender)
    ).order_by(
        Chat.created_at.desc()  # Most recent chats first
    )
    
    result = db.execute(query)
    chats = result.scalars().unique().all()
    
    return chats


def get_worshiper_chats(
    db: Session,
    worshiper_id: int
) -> list[Chat]:
    """
    Get all chats for a worshiper (inbox view).
    
    Real-world use case:
    Worshiper opens their inbox to see all leaders they've messaged.
    Chats are ordered by most recent message.
    
    Returns:
        list[Chat]: Chats with participant info and messages
    """
    # Get all chats where user is the worshiper
    query = select(Chat).where(
        Chat.worshiper_id == worshiper_id
    ).options(
        joinedload(Chat.worshiper),
        joinedload(Chat.leader),
        joinedload(Chat.messages).joinedload(Message.sender)
    ).order_by(
        Chat.created_at.desc()  # Most recent chats first
    )
    
    result = db.execute(query)
    chats = result.scalars().unique().all()
    
    return chats


def mark_messages_as_read(
    db: Session,
    chat_id: int,
    user_id: int
) -> int:
    """
    Mark all unread messages in a chat as read for the current user.
    
    Real-world use case:
    When a user opens a chat, all messages sent by the other person
    are marked as read. This updates unread counts and notification badges.
    
    Returns:
        int: Number of messages marked as read
    """
    from sqlalchemy import update
    
    # Mark all messages in this chat as read where:
    # 1. The message was sent by someone else (not the current user)
    # 2. The message is currently unread (is_read = 0)
    stmt = (
        update(Message)
        .where(
            and_(
                Message.chat_id == chat_id,
                Message.sender_id != user_id,
                Message.is_read == False
            )
        )
        .values(is_read=True)
    )
    
    result = db.execute(stmt)
    db.commit()
    
    return result.rowcount


def get_unread_count_for_chat(
    db: Session,
    chat_id: int,
    user_id: int
) -> int:
    """
    Get count of unread messages in a chat for a specific user.
    
    Returns count of messages sent by the OTHER person that haven't been read yet.
    """
    from sqlalchemy import func, select
    
    query = select(func.count(Message.id)).where(
        and_(
            Message.chat_id == chat_id,
            Message.sender_id != user_id,
            Message.is_read == False
        )
    )
    
    result = db.execute(query)
    return result.scalar() or 0
