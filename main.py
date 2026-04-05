from fastapi import FastAPI
import models
from database import engine

# Import all of our routers
from routers import users, records, dashboard

# 1. This magically creates our SQLite 'finance.db' file 
# and builds all the tables defined in our models.py automatically!
models.Base.metadata.create_all(bind=engine)

# 2. Start the FastAPI App
app = FastAPI(
    title="Zorvyn Finance Dashboard API",
    description="A Role-Based API for processing and aggregating financial records.",
    version="1.0.0"
)

# 3. Plug in all of the routes we built during Phase 5!
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)

# Basic health check endpoint
@app.get("/")
def read_root():
    return {"message": "Zorvyn Finance API is Running!"}
