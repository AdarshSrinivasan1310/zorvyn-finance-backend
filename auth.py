from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

# Secret keys for signing JWTs. In a real app, this MUST be in an .env file!
SECRET_KEY = "dummy_secret_key_for_intern_assignment"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Passlib configuration to hash passwords using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- PASSWORDS ---

# Uses bcrypt to completely scramble a user's password before we store it
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Checks if the user's plain-text attempt matches the scrambled hash in the database
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT TOKENS ---

# Generates the 'Keycard' for our hotel analogy
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Make a copy of whatever data we want to embed inside the token (like their username and role)
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Pack the expiration time into the token
    to_encode.update({"exp": expire})
    
    # Actually mathematically sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
