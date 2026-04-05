from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Create the internal connection to a SQLite file called finance.db
# check_same_thread is set to False strictly for SQLite in FastAPI.
SQLALCHEMY_DATABASE_URL = "sqlite:///./finance.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. Create a tunnel (Session) to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create a Base class that all our future models will inherit from
Base = declarative_base()

# 4. Dependency function to give each API request a fresh database connection, 
#    and safely close it when the request is done.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
