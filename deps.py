from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
import models
import auth

# This tells FastAPI that our API uses tokens.
# It also tells our Swagger Documentation to add an "Authorize" button!
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# --- 1. Identity Check (Who are you?) ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # The default error if anything goes wrong with the token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Un-seal the token using our secret key
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        
        # 2. Extract the username from the un-sealed token
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        # If the token is fake or expired, it immediately fails
        raise credentials_exception
    
    # 3. Look up the user in the database
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    # 4. Enforce the "Active/Inactive" status rule here!
    if not user.is_active:
        raise HTTPException(status_code=400, detail="This user account is inactive")
        
    return user


# --- 2. Concept Check (What are you allowed to do?) ---

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: models.User = Depends(get_current_user)):
        # If the user's role is not in our approved list, kick them out!
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}"
            )
        return user
