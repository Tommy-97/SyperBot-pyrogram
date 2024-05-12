# database.py
# import asyncio
import logging

import aiosqlite
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_URL = "sqlite+aiosqlite:///F:/SQLite/base.db"

engine = create_async_engine(SQLALCHEMY_URL, echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True
)


async def add_user(name, email):
    try:
        async with aiosqlite.connect(SQLALCHEMY_URL) as connection:
            cursor = await connection.execute('SELECT * FROM users WHERE email = ?', (email,))
            existing_user = await cursor.fetchone()
            if existing_user:
                logger.info("User with this email already exists.")
                return
            await connection.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
            await connection.commit()
            logger.info("User added successfully!")
    except Exception as e:
        logger.error(f"Failed to add user: {e}")


async def get_user_by_email(email):
    try:
        async with aiosqlite.connect(SQLALCHEMY_URL) as db:
            cursor = await db.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = await cursor.fetchone()
            return user
    except Exception as e:
        logger.error(f"An error occurred while getting user by email: {e}")
        return None


async def create_new_user(name, email):
    async with async_session() as session:
        try:
            new_user = User(name=name, email=email)
            session.add(new_user)
            await session.commit()
            logger.info("User added successfully!")
        except IntegrityError:
            logger.error("User with this email already exists.")
        except Exception as e:
            logger.error(f"An error occurred while creating a new user: {e}")
            session.rollback()
