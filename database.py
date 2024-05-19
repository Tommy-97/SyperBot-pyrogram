# database.py
import asyncio
import logging
import os
from datetime import datetime
from sqlite3 import IntegrityError

import aiosqlite
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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


async def add_user(name, email, status='alive'):
    async with async_session() as session:
        async with session.begin():
            # Проверка, существует ли пользователь с данным email
            result = await session.execute(text("SELECT * FROM users WHERE email = :email"), {'email': email})
            existing_user = result.scalar()
            if existing_user:
                logger.info("User with this email already exists.")
                return
            # Создание нового пользователя с указанным статусом
            new_user = User(name=name, email=email, status=status)
            session.add(new_user)
        logger.info("User added successfully!")


async def get_user_by_email(email):
    async with async_session() as session:
        try:
            result = await session.execute(text('SELECT * FROM users WHERE email = :email'), {'email': email})
            user = await result.fetchone()
            return user
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while getting user by email: {e}")
            return None


async def add_new_user(connection, name, email):
    try:
        await add_user(name, email)
    except Exception as e:
        logger.error(f"Error occurred while adding user: {e}")


async def add_new_user_by_email(connection, email):
    try:
        existing_user = await get_user_by_email(email)
        if existing_user:
            logger.info(f"User with email '{email}' already exists.")
        else:
            await add_new_user(connection, "Default Name", email)
            logger.info(f"New user with email '{email}' added successfully.")
    except Exception as e:
        logger.error(
            f"An error occurred while adding a new user by email: {e}")


async def add_new_user_with_async_session(name, email):
    try:
        async with async_session() as session:
            user = User(name=name, email=email)
            session.add(user)
            await session.commit()
            logger.info("User added successfully!")
    except IntegrityError:
        logger.error("User with this email already exists.")
    except Exception as e:
        logger.error(f"Failed to add user: {e}")


async def get_alive_users():
    async with async_session() as session:
        try:
            result = await session.execute(text('SELECT * FROM users WHERE status = :status'), {'status': 'alive'})
            users = result.scalars().all()
            return users
        except SQLAlchemyError as e:
            logger.error(
                f"SQLAlchemy error occurred while fetching alive users: {e}")
            return []


async def add_alive_user(name, email):
    try:
        await add_user(name, email)
    except (Exception, SQLAlchemyError) as e:
        logger.error(f"Error occurred while adding user: {e}")
        return []
    except Exception as e:
        logger.error(f"Error occurred while fetching alive users: {e}")
        raise


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
    asyncio.create_task(check_users_ready(bot_instance)
                        )  # Запуск в фоновом режиме

    await bot_instance.start()  # Запуск бота


async def check_users_ready(bot):
    while True:
        try:
            logging.info("Checking users...")
            active_users = await get_alive_users()
            if active_users:
                for user in active_users:
                    await send_message(bot, user.id, "Hello! It's time to check in.")
            else:
                logging.info("No active users found with status 'alive'.")
            await asyncio.sleep(60)
        except SQLAlchemyError as e:
            logging.error(
                f"SQLAlchemy error occurred while checking users: {e}")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while checking users: {e}")


async def send_message(bot, user_id, text):
    try:
        await bot.send_message(user_id, text)
        logging.info(f"Message sent to user {user_id}: {text}")
    except Exception as e:
        logging.error(f"Failed to send message to user {user_id}: {e}")

if __name__ == "__main__":
    try:
        # Создаем экземпляр бота
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
