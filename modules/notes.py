from modules.database import SessionLocal
from modules.models import Note

def create_note(content, user_id):
    db = SessionLocal()
    new_note = Note(content=content, user_id=user_id)
    db.add(new_note)
    db.commit()
    db.close()
    return True

def get_notes(user_id):
    db = SessionLocal()
    # Fetch all notes belonging to this specific user
    notes = db.query(Note).filter(Note.user_id == user_id).all()
    db.close()
    return notes