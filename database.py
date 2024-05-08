# database.py
import logging

from sqlalchemy import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SQLALCHEMY_URL = "sqlite+aiosqlite:///F:/SQLete/base.db"


engine = create_async_engine(SQLALCHEMY_URL, echo=True, future=True, connect_args={
                             "check_same_thread": False})


async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True)
