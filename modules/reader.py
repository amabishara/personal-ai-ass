from modules.database import SessionLocal
from modules.models import ReaderEntry


def create_reader_entry(title, content, user_id, book_title="Digital Body Language"):
    db = SessionLocal()
    entry = ReaderEntry(
        title=title,
        content=content,
        user_id=user_id,
        book_title=book_title,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    db.close()
    return entry


def get_reader_entries(user_id):
    db = SessionLocal()
    entries = (
        db.query(ReaderEntry)
        .filter(ReaderEntry.user_id == user_id)
        .order_by(ReaderEntry.created_at.desc())
        .all()
    )
    db.close()
    return entries
