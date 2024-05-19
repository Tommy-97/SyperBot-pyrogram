# handlers.py
import logging
from tkinter import Message

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.exc import IntegrityError

from database import add_user, async_session, check_users_ready
from models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin_ids = [180336418]  # [20285228] # Ваш Telegram ID


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
        async with async_session() as session:
            new_user = User(name=name, email=email)
            session.add(new_user)
            await session.commit()
            await message.reply_text(f"Пользователь {name} успешно добавлен в базу данных!")
    except IntegrityError:
        await message.reply_text("Пользователь с таким email уже существует!")
    except Exception as e:
        logger.exception("Error occurred while adding user")
        await message.reply_text("Произошла ошибка при добавлении пользователя. Пожалуйста, попробуйте позже.")


async def check_users_ready_command(client: Client, message):
    logger.info(
        f"Received /check_users_ready command from user {message.from_user.id}")
    if message.from_user is None:
        await message.reply("This command can only be used in a direct chat with the bot.")
        return

    if message.from_user.id in admin_ids:
        await message.reply("Checking users ready.")
        await check_users_ready(client)
    else:
        logger.info(
            f"User {message.from_user.id} is not authorized to use this command.")
        await message.reply("You are not authorized to use this command.")
