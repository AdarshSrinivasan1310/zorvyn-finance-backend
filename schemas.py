from pydantic import BaseModel
from typing import Optional, Literal, List, Dict
from datetime import datetime

# --- USER SCHEMAS ---

# 1. Received from the client when creating a user (Notice it requires a password!)
class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["Admin", "Analyst", "Viewer"] = "Viewer" # Default role if none provided

# 2. Sent back to the client (Notice it DOES NOT have the password!)
class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

# --- RECORD SCHEMAS ---

# 1. Received from the client to create a record
class RecordCreate(BaseModel):
    amount: float
    record_type: Literal["Income", "Expense"]
    category: str
    notes: Optional[str] = None

# 2. Sent back to the client
class RecordResponse(RecordCreate):
    id: int
    date: datetime
    owner_id: int
    is_deleted: bool

    class Config:
        from_attributes = True

# --- DASHBOARD SCHEMAS (Required for strict serialization) ---
class MonthlyTrend(BaseModel):
    month: str
    type: str
    total: float

class DashboardResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    category_breakdown: Dict[str, float]
    recent_activity: List[RecordResponse]
    monthly_trends: List[MonthlyTrend]

# --- AUTHENTICATION SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str
