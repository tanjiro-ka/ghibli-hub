from fastapi import FastAPI
from .auth.github import router as github_auth_router

app = FastAPI(title="GhibliHub API")

# Include auth routes
app.include_router(github_auth_router)

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}
