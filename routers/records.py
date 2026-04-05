from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

import models
import schemas
from database import get_db
from deps import RoleChecker, get_current_user

router = APIRouter(prefix="/records", tags=["Financial Records"])

admin_only = RoleChecker(["Admin"])
analyst_and_admin = RoleChecker(["Analyst", "Admin"])

# --- 1. CREATE A RECORD (ADMIN ONLY) ---
@router.post("/", response_model=schemas.RecordResponse)
def create_record(record: schemas.RecordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    new_record = models.Record(**record.model_dump(), owner_id=current_user.id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

# --- 2. GET & FILTER RECORDS (ANALYST & ADMIN) includes Pagination & Date filtering! ---
@router.get("/", response_model=List[schemas.RecordResponse])
def get_records(
    search: Optional[str] = Query(None, description="Optional Search Enhancement: Search inside notes"),
    category: Optional[str] = Query(None, description="Filter by Category"),
    record_type: Optional[str] = Query(None, description="Income or Expense"),
    start_date: Optional[datetime] = Query(None, description="Filter from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter up to this date"),
    skip: int = Query(0, ge=0, description="Pagination: Skip this many records"),
    limit: int = Query(100, le=100, description="Pagination: Return max this many records"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(analyst_and_admin)
):
    query = db.query(models.Record).filter(models.Record.is_deleted == False)
    
    if category: query = query.filter(models.Record.category == category)
    if record_type: query = query.filter(models.Record.record_type == record_type)
    if start_date: query = query.filter(models.Record.date >= start_date)
    if end_date: query = query.filter(models.Record.date <= end_date)
    
    # Optional Search Support Enhancement (Checks both Notes OR Category)
    if search:
        query = query.filter(or_(
            models.Record.notes.contains(search),
            models.Record.category.contains(search)
        ))
        
    # Apply Pagination
    return query.offset(skip).limit(limit).all()

# --- 3. UPDATE A RECORD (ADMIN ONLY) ---
@router.put("/{record_id}", response_model=schemas.RecordResponse)
def update_record(record_id: int, record_data: schemas.RecordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    record = db.query(models.Record).filter(models.Record.id == record_id, models.Record.is_deleted == False).first()
    if not record: 
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Update all fields provided
    for key, value in record_data.model_dump().items():
        setattr(record, key, value)
        
    db.commit()
    db.refresh(record)
    return record

# --- 4. SOFT DELETE A RECORD (ADMIN ONLY) ---
@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    record = db.query(models.Record).filter(models.Record.id == record_id, models.Record.is_deleted == False).first()
    if not record: 
        raise HTTPException(status_code=404, detail="Record not found")
        
    record.is_deleted = True 
    db.commit()
    return {"message": "Record safely soft-deleted"}
