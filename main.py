# main.py
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

from config import API_HASH, API_ID
from database import add_user, check_users_ready, create_users_table
from handlers import (add_user_command_handler, check_users_ready_command,
                      start_button_handler, start_command_handler)

logging.basicConfig(level=logging.INFO)


async def main():
    await create_users_table()  # Создание таблицы перед использованием
    await add_user("SyperBOT3000", "user@gmail.com", status='alive')
    await add_user("BOT3000", "another_email@mail.ru", status='alive')

    # Создаем экземпляр бота
    bot = Client("SuperChatMaster3000_bot", api_id=API_ID, api_hash=API_HASH)

    # Добавление обработчиков с корректными фильтрами
    bot.add_handler(MessageHandler(
        start_command_handler, filters.command("start")))
    bot.add_handler(CallbackQueryHandler(start_button_handler, filters.create(
        lambda _, __, query: query.data == b"start")))
    bot.add_handler(MessageHandler(
        add_user_command_handler, filters.command("add_user")))
    bot.add_handler(MessageHandler(check_users_ready_command,
                    filters.command("check_users_ready")))

    # Запуск проверки пользователей
    asyncio.create_task(check_users_ready(bot))  # Запуск в фоновом режиме

    await bot.start()  # Запуск бота

    logging.info("Bot started. Running indefinitely...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"RuntimeError: {e}")
        logging.info("Restarting the program...")
        asyncio.run(main())
