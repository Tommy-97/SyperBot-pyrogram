import asyncio
import logging
from sqlite3 import IntegrityError

import aiosqlite
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_URL = "sqlite+aiosqlite:///C:/Program Files/SQLiteStudio/postbase.db"

engine = create_async_engine(SQLALCHEMY_URL, echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True
)


async def create_users_table():
    try:
        async with aiosqlite.connect(SQLALCHEMY_URL) as conn:
            cursor = await conn.cursor()
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    status_updated_at DATETIME
                )
            ''')
            await conn.commit()
            logging.info("Users table created successfully.")
    except aiosqlite.Error as e:
        logging.error(f"Error creating users table: {e}")
        # Дополнительно распечатываем traceback для получения подробной информации об ошибке
        import traceback
        logging.error(traceback.format_exc())


async def main():
    await create_users_table()

# Run the main function
asyncio.run(main())


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
    except aiosqlite.Error as e:
        logger.error(f"Failed to add user: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding user: {e}")


async def get_user_by_email(email):
    try:
        async with aiosqlite.connect(SQLALCHEMY_URL) as db:
            cursor = await db.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = await cursor.fetchone()
            return user
    except aiosqlite.Error as e:
        logger.error(f"An error occurred while getting user by email: {e}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error occurred while getting user by email: {e}")
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
        except aiosqlite.Error as e:
            logger.error(f"An error occurred while creating a new user: {e}")
            session.rollback()
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while creating a new user: {e}")
            session.rollback()
