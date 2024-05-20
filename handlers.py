# handlers.py
import asyncio
import logging

from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.exc import IntegrityError

from database import add_user, async_session, check_users_ready
from models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_command_handler(client, message):
    logger.info("Received /start command")
    await message.reply_text(
        "Привет! Я бот. Нажми кнопку \"Старт\", чтобы начать.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Старт", callback_data="start")]]
        )
    )
    logger.info("Sent start message with inline keyboard")


async def start_button_handler(client, callback_query):
    logger.info("Received start button callback")
    await callback_query.message.reply_text("Вы нажали кнопку \"Старт\"!")


async def add_user_command_handler(client, message):
    logger.info("Received /add_user command")
    if len(message.command) != 3:
        await message.reply_text("Используйте команду в формате /add_user <имя> <email>")
        return
    name, email = message.command[1:3]
    try:
        await add_user(name, email)
        await message.reply_text(f"Пользователь {name} успешно добавлен в базу данных!")
    except IntegrityError:
        await message.reply_text("Пользователь с таким email уже существует!")
    except Exception as e:
        logger.exception("Error occurred while adding user")
        await message.reply_text("Произошла ошибка при добавлении пользователя. Пожалуйста, попробуйте позже.")


async def add_alive_user_command_handler(client, message):
    logger.info("Received /add_alive_user command")
    if len(message.command) != 3:
        await message.reply_text("Используйте команду в формате /add_alive_user <имя> <email>")
        return
    name, email = message.command[1:3]
    try:
        await add_user(name, email, status='alive')
        await message.reply_text(f"Пользователь {name} со статусом 'alive' успешно добавлен в базу данных!")
    except IntegrityError:
        await message.reply_text("Пользователь с таким email уже существует!")
    except Exception as e:
        logger.exception("Error occurred while adding user")
        await message.reply_text("Произошла ошибка при добавлении пользователя. Пожалуйста, попробуйте позже.")


async def check_users_ready_command(client: Client, message: Message):
    logger.info(
        f"Received /check_users_ready command from user {message.from_user.id}")
    admin_ids = [180336418]  # Replace with actual admin IDs

    if message.from_user.id not in admin_ids:
        await message.reply("You are not authorized to use this command.")
        logger.info(
            f"User {message.from_user.id} is not authorized to use this command.")
        return

    await message.reply("Checking users ready.")
    asyncio.create_task(check_users_ready(client))
