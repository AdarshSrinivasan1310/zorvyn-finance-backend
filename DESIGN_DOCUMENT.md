# Backend Engineering Design & Architecture Journal

This document serves as the engineering notebook for the Zorvyn backend assignment. It explicitly documents the architectural thought process, technical tradeoffs, and security considerations made throughout development.

## 1. Database & ORM Strategy
* **Selection:** SQLite was used to satisfy the "simplicity" requirement of the assignment, allowing evaluators to run the backend instantly without pulling Docker containers for PostgreSQL.
* **ORM (SQLAlchemy):** Rather than writing raw SQL strings, SQLAlchemy was implemented. This natively protects against SQL Injection attacks and allows the codebase to perfectly migrate to PostgreSQL in a production environment simply by altering the `DATABASE_URL` string in `database.py`.

## 2. Security & Authentication
* **JWT (Stateless):** Implemented stateless JSON Web Tokens encoded with Python-JOSE. This decision was made because stateless tokens make the backend infinitely horizontally scalable without needing a centralized session database (like Redis).
* **Bcrypt Hashing:** Passwords are mathematically hashed before touching the database. *(Note: Downgraded `bcrypt` to version `4.0.1` specifically to bypass a known modern dependency bug within the `passlib` validation matrix).*

## 3. Role-Based Access Control (RBAC) via Dependency Injection
* Unlike generic role-checking logic cluttered inside endpoint definitions, RBAC was abstracted into a reusable `RoleChecker` dependency injection class (`deps.py`).
* **Why?** This perfectly separates Authorization logic from Business logic. Endpoints like `DELETE /records/{id}` simply declare `Depends(RoleChecker(["Admin"]))` as a parameter, and FastAPI intercepts unauthorized variables automatically.

## 4. Advanced Data Integrity (Pydantic Rigidity)
* **The Problem:** It is common for APIs to fail silently if an invalid string is passed (e.g., passing `"record_type": "string1"`), polluting the database with orphaned math.
* **The Solution:** Added highly restrictive Pydantic schemas using Python's `Literal` typing. If an evaluator attempts to send `"Income "` instead of exactly `"Income"`, the Pydantic serialization layer rejects the payload with a native `422 Unprocessable Entity` before the request is even routed to the backend logic.
* **Response Serialization:** Added explicit `DashboardResponse` contracts to the dashboard. The application does not return raw SQLAlchemy models; it forces ORM structures through rigid Pydantic typing to ensure the API contracts remain stable for frontline consumers.

## 5. Dashboard Aggregations: Database vs. Memory Tradeoff
* **Implementation:** The Dashboard summary metrics use strict SQLAlchemy mathematical aggregations (`func.sum`, `group_by`, `func.strftime`) directly at the SQLite disk execution level.
* **Tradeoff:** It is easier to query all records via `db.query.all()` into a Python list and simply loop over them to calculate sums. However, that approach consumes catastrophic server memory at scale (O(n) space complexity). Executing the math directly inside the Database engine trades minor query complexity for extreme RAM efficiency. 

## 6. Financial Audit Trails (Soft Deletion)
* Financial records are never truly `DELETE`'d natively from the database. Instead, an `is_deleted` boolean flag is toggled to `True`.
* **Why?** In true strict Fintech environments, permanently erasing transaction history destroys compliance audit trails. All endpoints are configured to dynamically filter `is_deleted == False`.

## 7. Extended Free-Text Search Engine
* Rather than strictly querying a single `note` column, the Search parameter uses an `or_` SQLAlchemy clause. A user querying `search=Salary` dynamically filters both the `category` text and the `notes` text simultaneously, maximizing UX flexibility.

## 8. Development Tradeoff: Open Registration Security
* For the ease of assessment execution, the registration endpoint openly allows self-assigning the "Admin" role so evaluators can test the entire RBAC flow out-of-the-box. 
* In a rigorous production environment, initial Admin bootstrapping is strictly locked behind internal CLI provisioning tools, and dynamic Admin creation is protected behind heavy Authorization middleware.
