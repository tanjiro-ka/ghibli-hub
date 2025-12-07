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
│  │  └─ user.py       # User SQLAlchemy model
│  ├─ alembic/
│  │  └─ versions/     # Alembic migrations
├─ Dockerfile          # Dockerfile for FastAPI
├─ requirements.txt    # Python dependencies
docker-compose.yml     # Compose file for backend + PostgreSQL
```

### 🛠️ Requirements

- Docker Desktop
- Docker Compose v2
- (Optional) Python 3.11 locally if you want to run without Docker

Python dependencies are listed in `requirements.txt` and are installed inside the container.

### 🔐 Environment variables (.env)
Create a `.env` file in the project root (do NOT commit it). Example values are already in your local `.env` during development.

> [!IMPORTANT]
> Do NOT commit `.env` or any secret values (for example `GITHUB_CLIENT_SECRET` or `SECRET_KEY`) to version control.

Required variables (development):
```
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

Optional (defaults provided in `app/config.py`):
```
GITHUB_OAUTH_REDIRECT=http://localhost:8000/auth/github/callback
SECRET_KEY=dev-secret-key-change-in-production
```

### 🚀 Run the backend (Docker)

> [!IMPORTANT]
> Make sure Docker Desktop is running, then from the repository root:

```powershell
docker-compose down
docker-compose up --build -d
docker-compose logs api --tail 200
```

Open the API docs to inspect endpoints and payloads:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 🗄️ Database migrations (Alembic)
After the first build (or when you change models), run migrations:

```powershell
docker-compose exec api alembic upgrade head
```

This will create/update tables based on `alembic/versions`.

### 🔁 OAuth (GitHub) and session flow — what we implemented

This backend supports logging in with GitHub and returns JWTs to the frontend.

- `GET /auth/github/login` — Redirects the user to GitHub to authorize the app.
- `GET /auth/github/callback` — GitHub redirects here with a `code` and `state`. The backend exchanges the `code` for a GitHub access token, fetches the user's profile/email, creates/updates the `User` in the DB, then issues two JWTs:
    - `access_token` (shorter lived, type `access`)
    - `refresh_token` (longer lived, type `refresh`)

-- `POST /auth/refresh` — Accepts JSON `{ "refresh_token": "<token>" }` and returns a new `access_token`.
-- `GET /auth/me` — Protected endpoint. Use `Authorization: Bearer <access_token>` to get the current user.

Implementation notes:
- The `state` parameter is generated on login for CSRF protection — in production you must persist & validate it (session or cache like Redis). Current implementation generates a random state but does not validate against server-side storage (acceptable for local dev only).
- Token lifetimes: access tokens are configured to expire in 7 days and refresh tokens in 30 days (see `app/auth/session.py`). **For production consider much shorter access token lifetimes (minutes to hours) and implement refresh-token rotation and revocation.**


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