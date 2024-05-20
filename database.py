# database.py
import asyncio
import logging
import select
from datetime import datetime, timedelta
from sqlite3 import IntegrityError

import aiosqlite
from pyrogram import Client
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from config import API_HASH, API_ID
from models import Base, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_URL = "sqlite+aiosqlite:///C:/User/bot_pyrogram/userssssbase.db"

# Создаем подключение к базе данных
engine = create_async_engine(SQLALCHEMY_URL, echo=True, future=True, connect_args={
                             "check_same_thread": False})
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True)


async def create_users_table():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        logger.info("Users table created")


async def add_user(name, email, status='dead'):
    async with async_session() as session:
        async with session.begin():
            # Проверка, существует ли пользователь с данным email
            result = await session.execute(text("SELECT * FROM users WHERE email = :email"), {'email': email})
            existing_user = result.all()
            if existing_user:
                logger.info("User with this email already exists.")
                return
            # Создание нового пользователя с указанным статусом
            new_user = User(name=name, email=email, status=status)
            session.add(new_user)
            await session.commit()
            logger.info(f"User {name} added successfully!")


async def get_alive_users():
    async with async_session() as session:
        try:
            result = await session.execute(text('SELECT * FROM users WHERE status = :status'), {'status': 'alive'})
            users = result.all()  # Заменяем метод scalars().all() на просто all()
            return users
        except SQLAlchemyError as e:
            logger.error(
                f"SQLAlchemy error occurred while fetching alive users: {e}")
            return []


async def check_users_ready(bot):
    while True:
        try:
            logging.info("Checking users...")
            active_users = await get_alive_users()
            if active_users:
                for user in active_users:
                    await send_message(bot, user.id, "Привет! Пора проверить чек!")
                    await update_user_status(user.id, 'alive')
            else:
                logging.info("No active users found with status 'alive'.")
            await asyncio.sleep(60)
        except SQLAlchemyError as e:
            logging.error(
                f"SQLAlchemy error occurred while checking users: {e}")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while checking users: {e}")


async def update_user_status(user_id, status):
    async with async_session() as session:
        async with session.begin():
            user = await session.get(User, user_id)
            if user:
                user.status = status
                await session.commit()
                logger.info(f"User {user_id} status updated to '{status}'")


async def send_message(bot, user_id, text):
    try:
        await bot.send_message(user_id, text)
        logging.info(f"Message sent to user {user_id}: {text}")
    except Exception as e:
        if "PEER_ID_INVALID" in str(e):
            logging.warning(
                f"Ignoring PEER_ID_INVALID error for user {user_id}")
        else:
            logging.error(f"Failed to send message to user {user_id}: {e}")


async def debug_users():
    async with async_session() as session:
        result = await session.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        for user in users:
            logger.info(f"User: {user}")


async def main(bot_instance):
    await create_users_table()
    await add_user("SyperBOT3000", "user@gmail.com", status='alive')
    await add_user("BOT3000", "another_email@mail.ru", status='alive')
    await debug_users()

    # Запуск проверки пользователей
    asyncio.create_task(check_users_ready(bot_instance))

    await bot_instance.start()

if __name__ == "__main__":
    try:
        bot_instance = Client("my_bot", api_id=API_ID, api_hash=API_HASH)
        asyncio.run(main(bot_instance))
    except RuntimeError as e:
        logging.error(f"RuntimeError: {e}")


# async def create_users_table():
 #   async with async_session() as session:
        # async with session.begin():
        # connection = await session.connection()
        # await connection.run_sync(Base.metadata.create_all)
        # User


# async def add_user(name, email):
 #   async with async_session() as session:
  #      async with session.begin():
   #         existing_user = await session.execute(User.select().where(User.email == email))
    #        if existing_user.scalar():
     #           logger.info("User with this email already exists.")
      #          return
        # Передаем значения name и email из аргументов функции
        #     new_user = User(name=name, email=email)
        #    session.add(new_user)
        # logger.info("User added successfully!")
