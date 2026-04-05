# Finance Data Processing and Access Control Backend

## Overview
This is a secure, role-based backend API for a financial dashboard application built using **FastAPI** and **SQLite**. It demonstrates clean architecture, separated presentation layers (Pydantic), strict Role-Based Access Control (RBAC), and database aggregation logic (SQLAlchemy).

## Architecture Choices & "Why"
1. **Framework (FastAPI)**: Selected over Django to explicitly demonstrate the implementation of custom Role-Based Access Control and Dependency Injection. 
2. **Database (SQLite + SQLAlchemy)**: Matches the "SQLite for simplicity" requirement while still using an ORM to prevent SQL Injection and ensure perfectly structured Python models. The app is easily scalable to PostgreSQL by changing one line of configuration in `database.py`.
3. **Strict Validation & Schemas (Pydantic)**: Prevents dirty data from entering business logic entirely. Leverages `Literal` types to strictly reject invalid payloads (e.g. invalid roles or record types) with native `422 Unprocessable Entity` responses. Also rigorously validates and serializes the complex nested ORM relationships in the `DashboardResponse`.
4. **Authentication (JWT + Bcrypt)**: Stateless authentication via JWT removes the need for database session-lookups. Passwords are mathematically hashed with bcrypt.

## Technical Decisions & Production Adjustments
1. **Security/Secrets**: The `SECRET_KEY` in `auth.py` is currently hardcoded as a dummy string strictly for the convenience of evaluating this assignment out-of-the-box. In a true production environment, this is moved to a `.env` file using `python-dotenv`.
2. **Open Admin Registration**: For the ease of assessment execution, the registration endpoint openly allows self-assigning the "Admin" role. In an actual production setting, Admin creation would be strictly locked behind internal CLI tooling or require programmatic authorization by an existing Admin.
3. **Automated Testing**: An integration script (`test_system.py`) is included to rigorously evaluate the system. Note: **The FastAPI server must already be running** via Uvicorn before executing the test script.

## Core Features Implemented
*   **User & Role Management**: 
    *   Dynamic RBAC (`Admin`, `Analyst`, `Viewer`).
    *   Admins can view and toggle user status (`active` vs `inactive`).
*   **Financial Records CRUD**: 
    *   Full Create, Read, Update, Delete capabilities (Admins only for mutating logic).
    *   **Advanced Searching & Filtering**: Highly robust query parameters allowing filtering by Date ranges, Category, Type, Pagination, and a complex free-text `search` that dynamically queries both the Notes *and* Category columns.
    *   **Soft Deletion**: Implemented an `is_deleted` flag instead of permanently destroying financial audit history.
*   **Dashboard Aggregations**: 
    *   Rather than pulling data into Python loops, SQLAlchemy uses `func.sum()` and `.group_by()` to calculate net balances and category breakdowns directly at the database level for maximum performance.
    *   Returns Recent Activity feeds natively sorted by descending dates.

## Important Data Constraints (Required Values)
To ensure the Access Control and Dashboard Aggregations function perfectly, you must provide exact string values for certain columns when creating data:
1. **User Roles (`role`)**: Must be exactly `"Admin"`, `"Analyst"`, or `"Viewer"`. Only an `Admin` can create entries.
2. **Record Type (`record_type`)**: Must be exactly `"Income"` or `"Expense"`. The dashboard database aggregations mathematically depend on these exact strings to calculate the Net Balance.

## How to Run the Server
1. Ensure Python 3.x is installed.
2. Initialize and activate your virtual environment (`venv`).
3. Run the fast Server:
   ```bash
   uvicorn main:app --reload
   ```
4. Open the documentation at `http://127.0.0.1:8000/docs` to test the API visually!

## Testing the API Operations (Swagger Walkthrough)
1. Search for **Users** > `POST /users/register`. Create a user with `Admin` role.
2. Click **Authorize** at the top. Login with that name/password to receive your JWT.
3. Search for **Users** > `GET /users/admin/all`. Test your Admin privileges by viewing the entire network roster.
4. Search for **Financial Records** > `POST /records/`. Create `Income` and `Expense` records. Unassigned roles will receive a `403 Forbidden`.
5. Search for **Dashboard Summary** > `GET /dashboard/summary`. See the highly optimized aggregated mathematics reflecting your transactions!
