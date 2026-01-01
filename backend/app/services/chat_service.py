from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, func, select
from app.models.chat import Message
from app.models.user import User
from app.schemas.chat import MessageCreate, ChatSession
from datetime import datetime

class ChatService:
    async def send_message(self, db: AsyncSession, message_in: MessageCreate, sender_id: int):
        db_message = Message(
            task_id=message_in.task_id,
            sender_id=sender_id,
            receiver_id=message_in.receiver_id,
            content=message_in.content
        )
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    async def get_history(self, db: AsyncSession, task_id: int):
        stmt = select(Message).where(Message.task_id == task_id).order_by(Message.created_at.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_sessions(self, db: AsyncSession, user_id: int):
        stmt = select(Message).where(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        sessions_dict = {}
        for msg in messages:
            task_id = msg.task_id
            other_user_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
            
            key = (task_id, other_user_id)
            if key not in sessions_dict or msg.created_at > sessions_dict[key].created_at:
                sessions_dict[key] = msg
        
        final_sessions = []
        for (task_id, other_user_id), last_msg in sessions_dict.items():
            user_stmt = select(User).where(User.id == other_user_id)
            user_result = await db.execute(user_stmt)
            other_user = user_result.scalar_one_or_none()
            
            unread_stmt = select(func.count(Message.id)).where(
                and_(
                    Message.task_id == task_id,
                    Message.receiver_id == user_id,
                    Message.is_read == False
                )
            )
            unread_result = await db.execute(unread_stmt)
            unread_count = unread_result.scalar() or 0
            
            final_sessions.append(ChatSession(
                task_id=task_id,
                other_user=other_user,
                last_message=last_msg.content,
                last_message_time=last_msg.created_at,
                unread_count=unread_count
            ))
        
        return sorted(final_sessions, key=lambda x: x.last_message_time, reverse=True)

chat_service = ChatService()
