# main.py
import asyncio
import logging

import pandas as pd
from pyrogram import Client

from config import API_HASH, API_ID


async def main():
    bot = Client("ChatMastersbot", api_id=API_ID, api_hash=API_HASH)

    await bot.start()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    asyncio.run(main())
