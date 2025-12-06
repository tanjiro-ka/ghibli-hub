## Backend

This is the backend of the "My Ghibli World" project, built with **FastAPI** and **PostgreSQL**, fully containerized using **Docker** and **Docker Compose**.

### 📂 File structure
```bash
backend/
├─ app/
│  ├─ main.py          # FastAPI application
│  ├─ database.py      # SQLAlchemy database configuration
|  ├─ models/
|  │  │   └─ user.py      # User SQLAlchemy model
|  ├─ alembic/
|  │  │   └─ versions/      # User SQLAlchemy model
|  |  │      │   └─ ff6a9fb76d1e_create_users_table.py/      # User SQLAlchemy model
├─ Dockerfile          # Dockerfile for FastAPI
├─ requirements.txt    # Python dependencies
docker-compose.yml     # Compose file for backend + PostgreSQL
```

### 🛠️ Requirements

- Docker Desktop
- Docker Compose v2  
- Python dependencies (`requirements.txt`):
    - fastapi
    - uvicorn
    - sqlalchemy
    - alembic
    - psycopg2-binary
- Optional: pgAdmin or any PostgreSQL GUI for visual database management

> [!NOTE]
> All Python dependencies are installed inside the container. You do NOT need a virtual environment locally to run the backend.

### 🚀 Run the backend
> [!IMPORTANT]
> Always make sure Docker Desktop is running before executing the `docker-compose up`. 

**From the root project** folder:
```bash
docker-compose up --build
```

This command will:
- Build the FastAPI Docker image (`backend/Dockerfile`)
- Start the FastAPI backend container (`api`)
- Start the PostgreSQL container (`db`)
- Map the necessary ports to your local machine

**Apply database migrations (once, after first clone):**

```bash
docker-compose exec api alembic upgrade head
```

This will create all tables in the database according to the migrations in `alembic/versions/`.

> [!NOTE]
> Alembic is a database migration tool for SQLAlchemy. 
> It manages changes to the database schema in a version-controlled way, 
> so you don't have to write raw SQL to create or modify tables.


### 🗄️ SQLAlchemy Database

SQLAlchemy is a Python ORM (Object Relational Mapper) that allows you to interact with the database using Python objects instead of writing raw SQL queries. It handles database connections, table mappings, and relationships, making backend development easier and more maintainable.

**Database configuration (inside `app/database.py`):**

- Engine: `engine = create_engine(DATABASE_URL, echo=True)`
- Session: `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
- Base class for models: `Base = declarative_base()`

**User model (`app/models/user.py`):**
- Fields:
    - id (primary key)
    - github_id (GitHub OAuth)
    - email (not public)
    - display_name
    - avatar_url (optional)
    - created_at, updated_at timestamps

- Alembic migrations used to create the table: `alembic/versions/ff6a9fb76d1e_create_users_table.py`

**Connect and test the database**
Use the CLI inside the API container. From another terminal, execute: 

```bash
docker-compose exec api python
```

This opens the Python interpreter, where you can run: 
```python
from app.database import engine
conn = engine.connect()
conn.close()
```

If no errors appear, the SQLAlchemy connection is working correctly. 

### 🗄️ PostgreSQL Database
**Environment Variables (`docker-compose.yml`):**
```yaml
POSTGRES_USER=ghibli_user
POSTGRES_PASSWORD=ghibli_password
POSTGRES_DB=ghibli_db
```

**Connect to the database**

`Option A: CLI inside the container`

```bash
docker exec -it ghibli_db psql -U ghibli_user -d ghibli_db
```

Test query:

```bash
SELECT NOW();
```

`Option B: GUI (I use pgAdmin)`

- **Host**: localhost
- **Port**: 5432
- **User**: ghibli_user
- **Password**: ghibli_password
- **Database**: ghibli_db

> [!TIP]
You can leave "postgres" as the maintenance database. Once connected, you will see your database `ghibli_db` in the pgAdmin tree and can run queries there.

### 🌐 FastAPI Endpoints
- API root: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs