import asyncio
import logging
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.errors import FloodWait
from sqlalchemy import select

from config import API_HASH, API_ID
from database import async_session
from models import User

logger = logging.getLogger(__name__)


async def send_message(bot, user_id, text):
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        logger.error(f"Error sending message to user {user_id}: {e}")


async def check_users_ready(bot):
    while True:
        try:
            async with async_session() as session:
                async with session.begin():
                    ready_users = await session.execute(select(User).filter(User.status == 'alive'))
                    for user in ready_users.scalars().all():
                        try:
                            delta = datetime.utcnow() - (user.status_updated_at or user.created_at)
                            if delta >= timedelta(minutes=39):
                                text = "прекрасно"
                                await send_message(bot, user.id, text)
                                user.status = 'finished'
                            elif delta >= timedelta(minutes=6):
                                text = "ожидать"
                                await send_message(bot, user.id, text)
                                user.status = 'dead'
                        except Exception as e:
                            logger.error(
                                f"Error processing user {user.id}: {e}")
            session.commit()
        except Exception as e:
            logger.error(f"Error occurred: {e}")

        await asyncio.sleep(60)
