## Backend

This is the backend of the "My Ghibli World" project, built with **FastAPI** and **PostgreSQL**, fully containerized using **Docker** and **Docker Compose**.

### 📂 File structure
```bash
backend/
├─ app/
│  └─ main.py          # FastAPI application
├─ Dockerfile          # Dockerfile for FastAPI
├─ requirements.txt    # Python dependencies
docker-compose.yml     # Compose file for backend + PostgreSQL
```

### 🛠️ Requirements

- Docker Desktop
- Docker Compose v2  
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

### 🌐 FastAPI Endpoints
- API root: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

### 🗄️ PostgreSQL Database
**Environment Variables (docker-compose.yml):**
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