import datetime
import logging

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String)
    status_updated_at = Column(DateTime)

    def __repr__(self):
        if self.name and self.email:
            return f"<User(name='{self.name}', email='{self.email}', created_at='{self.created_at}')>"
        else:
            return f"<User(id={self.id}, status={self.status})>"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(f"New user created: id={self.id}, status={self.status}")

    def update_status(self, new_status):
        self.status = new_status
        self.status_updated_at = datetime.datetime.utcnow()
        logger.info(
            f"User status updated: id={self.id}, new_status={self.status}")
