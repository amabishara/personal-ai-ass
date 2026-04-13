import bcrypt
import jwt
import datetime
from modules.database import SessionLocal
from modules.models import User
from config import SECRET_KEY

def register_user(name, email, password):
    db = SessionLocal()
    
    # Hash the password securely
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create the new user and save to database
    new_user = User(name=name, email=email, password_hash=hashed.decode('utf-8'))
    db.add(new_user)
    db.commit()
    db.close()
    return True

def login_user(email, password):
    db = SessionLocal()
    
    # Find the user by email
    user = db.query(User).filter(User.email == email).first()
    
    # Check if user exists and password matches
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        # Generate a secure token valid for 24 hours
        token = jwt.encode(
            {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
            SECRET_KEY,
            algorithm="HS256"
        )
        db.close()
        return token
    
    db.close()
    return None

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None