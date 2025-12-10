## Backend

This is the backend of the "GhibliHub" project, built with **FastAPI** and **PostgreSQL**, containerized using **Docker** and **Docker Compose**.

### 📂 File structure
```bash
backend/
├─ app/
│  ├─ main.py          # FastAPI application
│  ├─ config.py        # Loads .env and config values
│  ├─ database.py      # SQLAlchemy database configuration
│  ├─ auth/            # OAuth + session helpers
│  │  ├─ github.py     # GitHub OAuth routes
│  │  └─ session.py    # JWT helpers + dependency
│  ├─ models/
│  │  ├─ user.py       # User SQLAlchemy model
│  │  ├─ movie.py      # Movie SQLAlchemy model (from Ghibli API)
│  │  ├─ character.py  # Character SQLAlchemy model (from Ghibli API)
│  │  ├─ review.py     # Review SQLAlchemy model (user reviews on movies)
│  │  └─ associations.py # Association tables (movie_character many-to-many)
│  ├─ alembic/
│  │  ├─ env.py        # Alembic environment config
│  │  └─ versions/     # Alembic migrations
├─ Dockerfile          # Dockerfile for FastAPI
├─ requirements.txt    # Python dependencies
├─ README.md           # Backend documentation (this file)
docker-compose.yml     # Compose file for backend + PostgreSQL (in root project)
```

### 🛠️ Requirements

- Docker Desktop
- Docker Compose v2
- (Optional) Python 3.11 locally if you want to run without Docker

Python dependencies are listed in `requirements.txt` and are installed inside the container.

### 🔐 Environment variables (.env)
Create a `.env` file in the project root (do NOT commit it). Example values are already in your local `.env` during development.

> [!WARNING]
> Do NOT commit `.env` or any secret values (for example `GITHUB_CLIENT_SECRET` or `SECRET_KEY`) to version control. Use `.env.example` as a template.

Required variables (development):
```
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
POSTGRES_USER=ghibli_user
POSTGRES_PASSWORD=ghibli_password
POSTGRES_DB=ghibli_db
DATABASE_URL=postgresql://ghibli_user:ghibli_password@db:5432/ghibli_db
```

**Generating a secure `SECRET_KEY`:**

The `SECRET_KEY` is used to sign JWT tokens and must be a secure random string. Generate one using Python (recommended):

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and add it to your `.env`:
```
SECRET_KEY=xK8vZ2jN9mP4qR5sT6uV7wX8yA9bC0dE1fG2hH3iI4jJ5
```

> [!TIP]
> Alternative methods: `openssl rand -hex 32` or use https://randomkeygen.com/ (select "256-bit WPA Key"). For production, always use a unique, randomly generated key per environment.

Optional (defaults provided in `app/config.py`):
```
GITHUB_OAUTH_REDIRECT=http://localhost:8000/auth/github/callback
ACCESS_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### 🚀 Run the backend (Docker)

> [!IMPORTANT]
> Make sure Docker Desktop is running, then from the repository root:

```powershell
docker-compose down
docker-compose up --build -d
docker-compose logs api --tail 200
```

> [!TIP]
> If the container crashes, check logs with `docker-compose logs api` to see error messages.

Open the API docs to inspect endpoints and payloads:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 🚀 Run the backend locally (without Docker, optional)

If you prefer to develop locally without Docker:

1. Create a virtual environment and activate it:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Ensure PostgreSQL is running locally (or update `DATABASE_URL` in `.env` to point to a remote DB).

4. Run migrations:
   ```powershell
   cd app/
   alembic upgrade head
   ```

5. Start the server:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

API will be available at `http://localhost:8000`.

### 🗄️ Database models

The backend currently implements the following SQLAlchemy models:

- **User** — Authentication via GitHub OAuth. Stores user profile (email, display name, avatar).
- **Movie** — Studio Ghibli film data (title, description, director, producer, year, rating, images). Synced from the [Ghibli API](https://ghibliapi.vercel.app/).
- **Character** — Studio Ghibli characters (name, gender, age, eye color, hair color). Synced from the Ghibli API.
- **Review** — User reviews on movies (rating 1-5, optional text). One review per user per movie.
- **movie_character** — Association table linking Movies ↔ Characters (many-to-many).
- **MovieStatus** — User status tracking (watched, want to watch) for each movie.
- **UserFavoriteMovie** — User favorite movies (planned).
- **UserFavoriteCharacter** — User favorite characters (planned).

### 🗄️ Database migrations (Alembic)

> [!IMPORTANT]
> When running Alembic commands inside the Docker container, **always navigate to `app/`** where `alembic.ini` is located. This is due to the Docker volume mount configuration.

**Initial migration** (when DB is created):
```powershell
docker-compose exec api bash
cd app/
alembic upgrade head
exit
```

**After modifying models**, generate and apply new migrations:
```powershell
docker-compose exec api bash
cd app/
alembic revision --autogenerate -m "describe your changes"
# Review the migration file in alembic/versions/
alembic upgrade head
exit
```

Example:
```powershell
docker-compose exec api bash
cd app/
alembic revision --autogenerate -m "add movie status tracking"
alembic upgrade head
```

### 🔁 OAuth (GitHub) and session flow

This backend supports logging in with GitHub and returns JWTs to the frontend.

- `GET /auth/github/login` — Redirects the user to GitHub to authorize the app.
- `GET /auth/github/callback` — GitHub redirects here with a `code` and `state`. The backend exchanges the `code` for a GitHub access token, fetches the user's profile/email, creates/updates the `User` in the DB, then issues two JWTs:
    - `access_token` (shorter lived, type `access`)
    - `refresh_token` (longer lived, type `refresh`)

-- `POST /auth/refresh` — Accepts JSON `{ "refresh_token": "<token>" }` and returns a new `access_token`.
-- `GET /auth/me` — Protected endpoint. Use `Authorization: Bearer <access_token>` to get the current user.

Implementation notes:
- The `state` parameter is generated on login for CSRF protection — in production you must persist & validate it (session or cache like Redis). Current implementation generates a random state but does not validate against server-side storage (acceptable for local dev only).
- Token lifetimes: access tokens are configured to expire in 7 days and refresh tokens in 30 days (see `app/auth/session.py`).

> [!WARNING]
> For production, use much shorter access token lifetimes (minutes to hours) and implement refresh-token rotation and revocation.


### 🔬 How to test the flow locally

1. Open in browser and start login:
     - `http://localhost:8000/auth/github/login`
     - Authorize the app on GitHub.
2. After redirect, the backend will return JSON with `access_token` and `refresh_token`.
3. Call protected endpoint with the access token (PowerShell example):

```powershell
#$ACCESS contains the access token returned in step 2
Invoke-RestMethod -Uri 'http://localhost:8000/auth/me' -Headers @{ Authorization = "Bearer $ACCESS" }
```

4. Refresh an access token using the refresh token (PowerShell example):

```powershell
#$REFRESH contains the refresh token returned in step 2
$body = @{ refresh_token = $REFRESH } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8000/auth/refresh' -Method Post -Body $body -ContentType 'application/json'
```

Alternative using `curl.exe` (Windows PowerShell) if you prefer `curl`:

```powershell
curl.exe -X POST -H "Content-Type: application/json" -d '{"refresh_token":"<REFRESH_TOKEN>"}' http://localhost:8000/auth/refresh
```

### ✅ Quick checklist for someone who clones the repo

- Clone repository
- Create `.env` with `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
- Start Docker: `docker-compose up --build -d`
- Run DB migrations: `docker-compose exec api alembic upgrade head`
- Open `http://localhost:8000/docs` to inspect endpoints and test OAuth (or use browser to start login)