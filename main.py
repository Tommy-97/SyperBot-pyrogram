# main.py
import asyncio
import logging

from pyrogram import Client
from pyrogram.errors import FloodWait

from bot import check_users_ready
from config import API_HASH, API_ID


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Client("ChatMastersbot", api_id=API_ID, api_hash=API_HASH)

    try:
        await bot.start()
        asyncio.create_task(check_users_ready(bot))
        while True:

            await asyncio.sleep(60)
    except FloodWait as e:
        wait_time = e.x
        logging.warning(
            f"Подождите {wait_time} секунд перед повторной попыткой")
        await asyncio.sleep(wait_time)
        await main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"RuntimeError: {e}")

        logging.info("Restarting the program...")
        asyncio.run(main())
