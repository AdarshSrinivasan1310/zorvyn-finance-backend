from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas
from database import get_db
from deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard Summary"])

# 1. GET AGGREGATED SUMMARY (Viewers, Analysts, and Admins can all access this mathematically)
@router.get("/summary", response_model=schemas.DashboardResponse)
def get_dashboard_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    # 1. Total Income & Expenses
    total_income = db.query(func.sum(models.Record.amount)).filter(models.Record.is_deleted == False, models.Record.record_type == "Income").scalar() or 0.0
    total_expenses = db.query(func.sum(models.Record.amount)).filter(models.Record.is_deleted == False, models.Record.record_type == "Expense").scalar() or 0.0

    # 2. Category Breakdown
    category_totals_query = db.query(models.Record.category, func.sum(models.Record.amount).label("total")).filter(models.Record.is_deleted == False).group_by(models.Record.category).all()
    category_breakdown = {category: total for category, total in category_totals_query}

    # 3. Recent Activity (Missing requirement fulfilled: Top 5 newest records!)
    recent_activity = db.query(models.Record).filter(models.Record.is_deleted == False).order_by(models.Record.date.desc()).limit(5).all()

    # 4. Monthly Trends (Final Missing Requirement: Group by Month and Type)
    # Using SQLite's strftime to group records by Year-Month
    monthly_trends_query = db.query(
        func.strftime('%Y-%m', models.Record.date).label("month"),
        models.Record.record_type,
        func.sum(models.Record.amount).label("total")
    ).filter(
        models.Record.is_deleted == False
    ).group_by(
        "month",
        models.Record.record_type
    ).all()
    
    # Format into a clean list of Pydantic dictionaries
    monthly_trends = [schemas.MonthlyTrend(month=row[0], type=row[1], total=row[2]) for row in monthly_trends_query if row[0]]

    # 5. Net Balance
    net_balance = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "category_breakdown": category_breakdown,
        "recent_activity": recent_activity,
        "monthly_trends": monthly_trends
    }

