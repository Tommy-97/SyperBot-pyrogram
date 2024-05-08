# bot.py
import asyncio
import logging
from datetime import datetime, timedelta

from pyrogram import Client

from config import API_HASH, API_ID
from database import Session
from models import User

logger = logging.getLogger(__name__)


async def send_message(bot, user_id, text):
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        logger.error(f"Error sending message to user {user_id}: {e}")


async def check_users_ready(bot):
    while True:
        async with Session() as session:
            ready_users = session.query(User).filter(
                User.status == 'alive').all()
            for user in ready_users:
                try:
                    if user.status_updated_at:
                        delta = datetime.utcnow() - user.status_updated_at
                    else:
                        delta = datetime.utcnow() - user.created_at

                    if delta >= timedelta(minutes=6):
                        if delta >= timedelta(minutes=39):
                            text = "прекрасно"
                            await send_message(bot, user.id, text)
                            user.status = 'finished'
                            logger.info(
                                f"Message sent to user {user.id}: {text}")
                        elif delta >= timedelta(minutes=6):
                            text = "ожидать"
                            await send_message(bot, user.id, text)
                            user.status = 'dead'
                            logger.info(
                                f"Message sent to user {user.id}: {text}")
                    session.commit()
                except Exception as e:
                    logger.error(f"Error processing user {user.id}: {e}")

        await asyncio.sleep(1)


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Client("ChatMastersbot", api_id=API_ID, api_hash=API_HASH)

    try:
        await bot.start()
        asyncio.create_task(check_users_ready(bot))
        await bot.idle()
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
