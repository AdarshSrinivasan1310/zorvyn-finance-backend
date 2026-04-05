from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

import models
import schemas
import auth
import deps
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

# --- 1. REGISTER NEW USER ---
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if a user with that username already exists
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    # Hash the password using our get_password_hash function from auth.py
    hashed_password = auth.get_password_hash(user.password)
    
    # Save the new user into our SQLAlchemy model!
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# --- 2. LOGIN TO RECEIVE TOKEN ---
# This endpoint specifically uses OAuth2PasswordRequestForm to stay compatible with Swagger UI
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Look up the user by username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    # Verify the incoming plain-text password against our hashed database password
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # If successful, pack their data into a new JWT token!
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# --- 3. GET MY PROFILE ---
# This proves that our middleware (deps.py) works!
@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

# --- 4. VIEW ALL USERS (ADMIN ONLY) ---
@router.get("/admin/all", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: models.User = Depends(deps.RoleChecker(["Admin"]))):
    return db.query(models.User).all()

# --- 5. DEACTIVATE OR ACTIVATE A USER (ADMIN ONLY) ---
@router.put("/{user_id}/status", response_model=schemas.UserResponse)
def update_user_status(user_id: int, is_active: bool = Query(..., description="Set True for Active, False for Inactive"), db: Session = Depends(get_db), current_user: models.User = Depends(deps.RoleChecker(["Admin"]))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot edit your own account status")
        
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user

# --- 6. CHANGE USER ROLE (ADMIN ONLY) ---
@router.put("/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(user_id: int, new_role: str = Query(..., pattern="^(Admin|Analyst|Viewer)$"), db: Session = Depends(get_db), current_user: models.User = Depends(deps.RoleChecker(["Admin"]))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot edit your own account role")
        
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


