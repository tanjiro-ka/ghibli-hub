import os
from dotenv import load_dotenv

# Load .env from root directory
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_OAUTH_REDIRECT = os.getenv("GITHUB_OAUTH_REDIRECT", "http://localhost:8000/auth/github/callback")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
    raise ValueError("GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set in .env")
