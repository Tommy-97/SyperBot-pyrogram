# bot.py
import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database import async_session
from models import User

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def send_message(bot, user_id, text):
    try:
        await bot.send_message(user_id, text)
        logger.info(f"Message sent to user {user_id}: {text}")
    except Exception as e:
        logger.error(f"Failed to send message to user {user_id}: {e}")


async def check_users_ready(bot):
    logging.info("Checking users...")
    try:
        async with async_session() as session:
            async with session.begin():
                ready_users = await session.execute(select(User).filter(User.status == 'alive'))
                for user in ready_users.scalars().all():
                    try:
                        logger.info(
                            f"User {user.id} with status 'alive' found.")
                        delta = datetime.utcnow() - (user.status_updated_at or user.created_at)
                        if delta >= timedelta(minutes=39):
                            text = "прекрасно"
                            await send_message(bot, user.id, text)
                            user.status = 'finished'
                            logger.info(
                                f"User {user.id} status updated to 'finished'.")
                        elif delta >= timedelta(minutes=6):
                            text = "ожидать"
                            await send_message(bot, user.id, text)
                            user.status = 'dead'
                            logger.info(
                                f"User {user.id} status updated to 'dead'.")
                    except Exception as e:
                        logger.error(f"Error processing user {user.id}: {e}")
                await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error occurred while checking users: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking users: {e}")

    await asyncio.sleep(60)
