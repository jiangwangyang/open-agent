import json
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from openagent.repository.database import ConversationEntity, MessageEntity
from openagent.repository.database import async_session


async def get_conversations() -> list[ConversationEntity]:
    async with async_session() as session:
        stmt = (
            select(ConversationEntity)
            .order_by(ConversationEntity.update_time.desc())
        )
        result = await session.execute(stmt)
        conversations = result.scalars().all()
        return conversations


async def get_conversation(conversation_id: int) -> ConversationEntity | None:
    async with async_session() as session:
        stmt = (
            select(ConversationEntity)
            .where(ConversationEntity.id == conversation_id)
            .options(selectinload(ConversationEntity.messages))
        )
        result = await session.execute(stmt)
        conversation = result.scalars().first()
        if not conversation:
            return None
        return conversation


async def save_conversation(title: str, work_dir: str) -> ConversationEntity:
    current_time = datetime.now()
    async with async_session() as session:
        conversation = ConversationEntity(
            title=title,
            work_dir=work_dir,
            create_time=current_time,
            update_time=current_time
        )
        session.add(conversation)
        await session.commit()
        return conversation


async def save_conversation_messages(conversation_id: int, messages: list):
    current_time = datetime.now()
    async with async_session() as session:
        # 1. 更新会话时间
        conversation = await session.get(ConversationEntity, conversation_id)
        conversation.update_time = current_time

        # 2. 批量插入 messages
        db_messages = [
            MessageEntity(
                conversation_id=conversation.id,
                role=msg["role"],
                content=json.dumps(msg["content"], ensure_ascii=False),
                time=current_time
            )
            for msg in messages
        ]
        session.add_all(db_messages)

        # 提交事务
        await session.commit()


async def delete_conversation(conversation_id: int):
    async with async_session() as session:
        stmt = delete(ConversationEntity).where(ConversationEntity.id == conversation_id)
        await session.execute(stmt)
        await session.commit()
