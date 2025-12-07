# 🎬 GhibliHub

A full-stack web application for **Studio Ghibli movie enthusiasts**. Organize, track, and review your favorite Studio Ghibli films and characters.

> [!NOTE]
> This is a **personal learning project** built to practice full-stack web development, database design, and API development. It is an independent educational project created to demonstrate software engineering skills and build portfolio experience. Not affiliated with or derived from any existing projects.

## 📋 Overview

**GhibliHub** is a web platform where users can:

- **Browse and explore** Studio Ghibli movies and characters (data fetched from the [Ghibli API](https://ghibliapi.vercel.app/))
- **Track viewing status** Mark movies as "watched" or "want to watch"
- **Write reviews** Leave personal ratings (1-5 stars) and comments on films you've seen
- **Manage favorites** Create personalized lists of favorite movies and characters
- **View user profiles** See your activity, review history, and curated collections
- **Authenticate via GitHub** Secure OAuth login integration

## 🏗️ Architecture

**GhibliHub** is built as a modern **full-stack application** with clear separation of concerns:

```
ghibli-hub/
├── backend/          # FastAPI + PostgreSQL (REST API)
├── frontend/         # React / Vue / etc. (UI - to be implemented)
└── docker-compose.yml # Orchestration
```

### **Backend** (`backend/`)
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy with Alembic migrations
- **Auth:** GitHub OAuth 2.0 + JWT sessions
- **Containerization:** Docker + Docker Compose

See [backend/README.md](./backend/README.md) for detailed backend documentation.

### **Frontend** (`frontend/`)
- To be implemented (planned)

## 🎯 Project Goals

### Phase 1: **Backend Infrastructure** ✅ In progress

> [!IMPORTANT]
> Focus is on building a solid, scalable backend with proper database design and API structure.

- [x] Project setup & Docker configuration
- [x] GitHub OAuth authentication
- [ ] Core data models (User, Movie, Character, Review, etc.)
- [ ] Database migrations
- [ ] REST API endpoints for CRUD operations

### Phase 2: **Frontend Development** ⏳ Planned
- [ ] React/Vue application setup
- [ ] Authentication UI (login flow)
- [ ] Movie/Character browse and search
- [ ] User profile and favorites
- [ ] Review creation & management

### Phase 3: **Advanced Features** 🔮 Future
- [ ] Community features (follow users, see friends' reviews)
- [ ] Advanced filtering and sorting
- [ ] Watchlist sharing
- [ ] Recommendation engine

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** (recommended for the cleanest experience)
- **Docker Compose v2**
- (Optional) **Python 3.11+** if running backend locally without Docker

### Setup and run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tanjiro-ka/ghibli-hub.git
   cd ghibli-hub
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your GitHub OAuth credentials (see [.env.example](./.env.example) for details).

> [!IMPORTANT]
> Never commit `.env` to version control. It contains sensitive secrets (OAuth tokens, database passwords, etc.).

3. **Start the application with Docker:**
   ```powershell
   docker-compose up --build -d
   ```

> [!TIP]
> First build may take a few minutes. Check logs with `docker-compose logs api --tail 50`

4. **Run database migrations:**
   ```powershell
   docker-compose exec api bash
   cd /app
   alembic upgrade head
   exit
   ```

5. **Access the API:**
   - Swagger UI (interactive docs): http://localhost:8000/docs
   - ReDoc (alternative docs): http://localhost:8000/redoc

### Test OAuth Flow

> [!NOTE]
> Make sure your GitHub OAuth app redirect URI matches exactly: `http://localhost:8000/auth/github/callback`

Once the backend is running:

1. Open your browser: http://localhost:8000/auth/github/login
2. Authorize the application on GitHub
3. You'll receive `access_token` and `refresh_token` in the response
4. Use the access token to call protected endpoints

Example (PowerShell):
```powershell
$token = "<your_access_token>"
Invoke-RestMethod -Uri 'http://localhost:8000/auth/me' `
  -Headers @{ Authorization = "Bearer $token" }
```

## 📁 Project Structure

```
my-ghibli-world/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── movie.py
│   │   │   ├── character.py
│   │   │   ├── review.py
│   │   │   └── associations.py
│   │   ├── auth/              # GitHub OAuth + JWT
│   │   ├── alembic/           # Database migrations
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Configuration & env vars
│   │   └── database.py        # SQLAlchemy setup
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md              # Backend documentation
├── frontend/                   # Frontend (TBA)
├── docker-compose.yml         # Docker Compose config
├── .env.example               # Example environment variables
├── .gitignore
└── README.md                  # This file
```

## 🔑 Key Features

### 1. **Authentication**
- Secure GitHub OAuth 2.0 login
- JWT-based session management
- Refresh token rotation (future improvement)

### 2. **Data Management**
- **Movies:** Synchronized from Ghibli API with rich metadata (director, producer, rating, synopsis, images)
- **Characters:** Linked to movies (many-to-many relationship)
- **Reviews:** User-generated ratings and comments (one per user per movie)
- **Tracking:** Watch status (watched, want to watch) and favorites

### 3. **REST API**
- Full CRUD operations for movies, characters, reviews
- Advanced filtering & pagination
- User profile endpoints
- Protected routes via JWT authentication

## 📚 Documentation

### Backend Development
For detailed backend setup, API endpoints, database schema, and migration instructions, see:
→ [backend/README.md](./backend/README.md)

### Environment Variables
See [.env.example](./.env.example) for all configurable variables.

### Database Schema
Entity-relationship diagram and detailed schema documentation (coming soon)

## 💧 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **API** | FastAPI | 0.104+ |
| **Language** | Python | 3.11+ |
| **Database** | PostgreSQL | 15 |
| **ORM** | SQLAlchemy | 2.0+ |
| **Migrations** | Alembic | Latest |
| **Auth** | GitHub OAuth 2.0 + JWT | - |
| **Containerization** | Docker & Compose | Latest |
| **Frontend** | React / Vue (TBA) | - |

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Create a feature branch** from `main`
2. **Follow the commit message convention:**
   ```
   feat(scope): description
   fix(scope): description
   docs(scope): description
   ```
3. **Update relevant tests and documentation**
4. **Open a Pull Request** with a clear description

See the [CONTRIBUTING.md](./CONTRIBUTING.md) file for detailed guidelines (coming soon).

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](./LICENSE) file for details.

## 🎎 Inspiration

This project celebrates the beautiful works of **Studio Ghibli** and is built using data from the public [Ghibli API](https://ghibliapi.vercel.app/). No official affiliation with Studio Ghibli.

## 📞 Contact and Support

- **Project repository:** https://github.com/tanjiro-ka/ghibli-hub
- **Issues and bug reports:** [GitHub Issues](https://github.com/tanjiro-ka/ghibli-hub/issues)
- **GitHub Projects:** Track our development roadmap [here](https://github.com/tanjiro-ka/ghibli-hub/projects)

---

**Happy coding! 🚀**
