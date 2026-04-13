from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from modules.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    preferences = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="pending")
    user_id = Column(Integer, ForeignKey("users.id"))

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))


class ReaderEntry(Base):
    __tablename__ = "reader_entries"

    id = Column(Integer, primary_key=True, index=True)
    book_title = Column(String, default="Digital Body Language")
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
