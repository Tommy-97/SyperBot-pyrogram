import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import API_HASH, API_ID
from database import async_session
from models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('dp.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


async def main():
    async with Client("ChatMastersbot", api_id=API_ID, api_hash=API_HASH) as bot:

        @bot.on_message(filters.command("start"))
        async def start_command(client, message):
            logger.info("Received /start command")
            await message.reply_text(
                "Привет! Я бот. Нажми кнопку \"Старт\", чтобы начать.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Старт", callback_data="start")]]
                )
            )

        @bot.on_callback_query(filters.regex("start"))
        async def start_button(client, callback_query):
            logger.info("Received start button callback")
            await callback_query.message.reply_text("Вы нажали кнопку \"Старт\"!")

        @bot.on_message(filters.private & filters.command("add_user"))
        async def add_user_command(client, message):
            logger.info("Received /add_user command")
            if len(message.command) != 3:
                await message.reply_text("Используйте команду в формате /add_user <имя> <email>")
                return
            name, email = message.command[1:3]
            async with async_session() as session:
                new_user = User(name=name, email=email)
                session.add(new_user)
                await session.commit()
            await message.reply_text(f"Пользователь {name} успешно добавлен в базу данных!")

        asyncio.create_task(main())
