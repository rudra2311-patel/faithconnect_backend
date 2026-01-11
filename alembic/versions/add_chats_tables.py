"""Add chats and messages tables for private messaging

Revision ID: add_chats_tables
Revises: add_comments_table
Create Date: 2024-01-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_chats_tables'
down_revision = 'add_comments_table'
branch_labels = None
depends_on = None


def upgrade():
    """
    Creates chats and messages tables for private async messaging.
    
    Business rules enforced at DB level:
    - One chat per worshiper-leader pair (unique constraint)
    - Messages immutable (no update/delete, cascade on chat delete only)
    - Explicit sender roles (WORSHIPER or LEADER)
    """
    
    # Create SenderRole enum
    sender_role_enum = postgresql.ENUM('WORSHIPER', 'LEADER', name='senderrole', create_type=True)
    sender_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Create chats table
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('worshiper_id', sa.Integer(), nullable=False),
        sa.Column('leader_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['worshiper_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leader_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        
        # Business rule: one chat per worshiper-leader pair
        sa.UniqueConstraint('worshiper_id', 'leader_id', name='uq_worshiper_leader_chat')
    )
    
    # Create indexes for common queries
    op.create_index('ix_chats_worshiper_id', 'chats', ['worshiper_id'])
    op.create_index('ix_chats_leader_id', 'chats', ['leader_id'])
    op.create_index('ix_chats_created_at', 'chats', ['created_at'])
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('sender_role', sender_role_enum, nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for message queries
    op.create_index('ix_messages_chat_id', 'messages', ['chat_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_index('ix_messages_chat_id_created_at', 'messages', ['chat_id', 'created_at'])


def downgrade():
    """Remove chats and messages tables"""
    
    # Drop tables
    op.drop_index('ix_messages_chat_id_created_at', 'messages')
    op.drop_index('ix_messages_created_at', 'messages')
    op.drop_index('ix_messages_chat_id', 'messages')
    op.drop_table('messages')
    
    op.drop_index('ix_chats_created_at', 'chats')
    op.drop_index('ix_chats_leader_id', 'chats')
    op.drop_index('ix_chats_worshiper_id', 'chats')
    op.drop_table('chats')
    
    # Drop enum
    sa.Enum(name='senderrole').drop(op.get_bind(), checkfirst=True)
