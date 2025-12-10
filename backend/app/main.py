from fastapi import FastAPI
from .auth.github import router as github_auth_router
from .routes.users import router as users_router

app = FastAPI(
    title="GhibliHub API",
    description="API for Studio Ghibli movie tracking platform",
    version="0.1.0"
)

# Include routers
app.include_router(github_auth_router)
app.include_router(users_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to GhibliHub API"}
