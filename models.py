from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

# The User table inheriting from our Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # For example: 'Viewer', 'Analyst', 'Admin'
    is_active = Column(Boolean, default=True) # User Status (Active/Inactive)

    
    # Establish a relationship with the Record table. 
    # This automatically gives us all records belonging to this user!
    records = relationship("Record", back_populates="owner")

# The Record table for financial entries
class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    record_type = Column(String) # 'Income' or 'Expense'
    category = Column(String) # e.g., 'Groceries', 'Salary'
    date = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(String, nullable=True) # Optional field
    is_deleted = Column(Boolean, default=False) # Optional Extra Points: Soft Delete

    
    # The Foreign Key linking back to the User who created it
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Let SQLAlchemy know that a Record belongs to a User
    owner = relationship("User", back_populates="records")
