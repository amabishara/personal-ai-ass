from modules.database import SessionLocal
from modules.models import User

def get_user_preferences(user_id):
    db = SessionLocal()
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    
    # Return their preferences if they have any, otherwise return an empty string
    if user and user.preferences:
        return user.preferences
    return "User prefers concise, helpful, and professional answers."

def update_user_preferences(user_id, new_preferences):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.preferences = new_preferences
        db.commit()
    db.close()
    return True