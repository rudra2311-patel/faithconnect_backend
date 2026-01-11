"""
Routes for private messaging between worshipers and leaders.

Enables asynchronous spiritual guidance through text messaging.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User, UserRole
from app.chats.schemas import (
    SendMessageRequest,
    MessageResponse,
    ChatResponse,
    ChatSummary,
    ChatsListResponse
)
from app.chats.models import Chat, Message
from app.chats.services import (
    get_or_create_chat,
    send_message,
    get_chat_with_messages,
    get_leader_chats,
    get_worshiper_chats
)
from app.chats.permissions import verify_follow_exists, verify_chat_participant


router = APIRouter(tags=["Chats"])


@router.post(
    "/chats/{chat_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
def send_message_to_chat(
    chat_id: int,
    message_data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message in an existing chat.
    
    Role Enforcement: CHAT PARTICIPANTS ONLY (HTTP 403 otherwise).
    
    Real-world use case:
    - Worshiper or leader responds in conversation
    - Message added to chat history
    - Other party can read when they check their inbox
    
    Faith-aligned async messaging:
    This is NOT real-time chat. Messages are designed for thoughtful
    spiritual guidance where both parties can take time to reflect
    before responding.
    
    Workflow:
    1. User must be a chat participant
    2. Message is saved with sender role
    3. Other party can read and respond when ready
    """
    # Get chat and verify participant
    chat = verify_chat_participant(db=db, chat_id=chat_id, user_id=current_user.id)
    
    # Send message
    message = send_message(
        db=db,
        chat=chat,
        sender_id=current_user.id,
        sender_role=current_user.role,
        message_data=message_data
    )
    
    return message


@router.post(
    "/leaders/{leader_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
def send_first_message_to_leader(
    leader_id: int,
    message_data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send first message to a leader (creates chat if needed).
    
    Role Enforcement: WORSHIPERS ONLY (leaders can't initiate).
    Follow Requirement: Worshiper must follow the leader.
    
    Real-world use case:
    - Worshiper sends first message: "I need guidance about prayer"
      → Chat is created automatically
    - Returns the message with chat_id
    - Worshiper can continue conversation using POST /chats/{chat_id}/messages
    
    Workflow:
    1. Worshiper must follow leader
    2. Chat is created if this is first message
    3. Message is saved
    4. Leader can see it in their inbox
    """
    # Role enforcement: only worshipers can initiate
    if current_user.role != UserRole.WORSHIPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only worshipers can initiate conversations with leaders"
        )
    
    worshiper_id = current_user.id
    
    # Verify worshiper follows this leader
    verify_follow_exists(db=db, worshiper_id=worshiper_id, leader_id=leader_id)
    
    # Get or create chat
    chat = get_or_create_chat(
        db=db,
        worshiper_id=worshiper_id,
        leader_id=leader_id
    )
    
    # Send message
    message = send_message(
        db=db,
        chat=chat,
        sender_id=current_user.id,
        sender_role=current_user.role,
        message_data=message_data
    )
    
    return message


@router.get("/chats/{chat_id}", response_model=ChatResponse)
def get_chat_conversation(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat conversation history.
    
    Role Enforcement: CHAT PARTICIPANTS ONLY (HTTP 403 otherwise).
    
    Real-world use case:
    User opens a conversation to see message history and continue
    the spiritual dialogue. Messages are ordered chronologically.
    
    Returns:
    - Chat info (participants, creation date)
    - All messages ordered oldest first (natural conversation flow)
    - Participant info (names, profile photos)
    
    UX: Full-screen chat view showing conversation history.
    """
    from sqlalchemy.orm import joinedload
    from sqlalchemy import select
    
    # Get chat and verify participant
    chat = verify_chat_participant(db=db, chat_id=chat_id, user_id=current_user.id)
    
    # Get full chat with messages
    stmt = (
        select(Chat)
        .options(
            joinedload(Chat.worshiper),
            joinedload(Chat.leader),
            joinedload(Chat.messages).joinedload(Message.sender)
        )
        .where(Chat.id == chat_id)
    )
    result = db.execute(stmt)
    chat_with_messages = result.unique().scalar_one_or_none()
    
    if not chat_with_messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return chat_with_messages


@router.get("/chats", response_model=ChatsListResponse)
def get_my_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get my chat inbox (auto-routes based on role).
    
    Role Enforcement: ALL AUTHENTICATED USERS.
    
    - Leaders get their inbox (all conversations with worshipers)
    - Worshipers get their inbox (all conversations with leaders)
    
    Real-world use case:
    Universal chat inbox - users see all their conversations with unread counts.
    """
    if current_user.role == UserRole.LEADER:
        chats = get_leader_chats(db=db, leader_id=current_user.id)
    else:
        chats = get_worshiper_chats(db=db, worshiper_id=current_user.id)
    
    # Build chat summaries with unread counts
    chat_summaries = []
    for chat in chats:
        # Get last message
        last_message = chat.messages[-1] if chat.messages else None
        
        # Count unread messages (messages sent by OTHER person that I haven't read)
        unread_count = sum(
            1 for msg in chat.messages
            if msg.sender_id != current_user.id and not msg.is_read
        )
        
        chat_summary = ChatSummary(
            id=chat.id,
            worshiper_id=chat.worshiper_id,
            leader_id=chat.leader_id,
            created_at=chat.created_at,
            worshiper=chat.worshiper,
            leader=chat.leader,
            last_message=last_message,
            unread_count=unread_count
        )
        chat_summaries.append(chat_summary)
    
    return ChatsListResponse(
        chats=chat_summaries,
        total=len(chat_summaries)
    )


@router.get("/leaders/chats", response_model=ChatsListResponse)
def get_leader_inbox(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Leader views their chat inbox.
    
    Role Enforcement: LEADERS ONLY (HTTP 403 for worshipers).
    
    Real-world use case:
    Leader opens their inbox to see all worshipers who have messaged them.
    Each chat shows worshiper info and last message for context.
    
    Returns:
    - List of chats ordered by most recent message
    - Each chat includes: worshiper info, last message preview
    - Total count of conversations
    
    UX: Inbox view similar to email, showing all active conversations.
    Leader can tap a chat to see full conversation.
    """
    # Role enforcement
    if current_user.role != UserRole.LEADER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders can access this endpoint"
        )
    
    # Get all chats for this leader
    chats = get_leader_chats(db=db, leader_id=current_user.id)
    
    # Build chat summaries with last message
    chat_summaries = []
    for chat in chats:
        # Get last message
        last_message = chat.messages[-1] if chat.messages else None
        
        # Count unread messages for this leader
        unread_count = sum(
            1 for msg in chat.messages
            if msg.sender_id != current_user.id and not msg.is_read
        )
        
        chat_summary = ChatSummary(
            id=chat.id,
            worshiper_id=chat.worshiper_id,
            leader_id=chat.leader_id,
            created_at=chat.created_at,
            worshiper=chat.worshiper,
            leader=chat.leader,
            last_message=last_message,
            unread_count=unread_count
        )
        chat_summaries.append(chat_summary)
    
    return ChatsListResponse(
        chats=chat_summaries,
        total=len(chat_summaries)
    )



@router.post("/chats/{chat_id}/mark-read", status_code=status.HTTP_204_NO_CONTENT)
def mark_chat_as_read(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all unread messages in a chat as read.
    
    Role Enforcement: CHAT PARTICIPANTS ONLY (HTTP 403 otherwise).
    
    Real-world use case:
    When a user opens a chat conversation, all messages from the other
    person are automatically marked as read. This updates notification
    badges and unread counts in the inbox.
    
    UX: Red notification badge disappears when user opens the chat.
    """
    from app.chats.services import mark_messages_as_read
    
    # Verify user is a participant
    verify_chat_participant(db=db, chat_id=chat_id, user_id=current_user.id)
    
    # Mark messages as read
    mark_messages_as_read(db=db, chat_id=chat_id, user_id=current_user.id)
    
    return None
