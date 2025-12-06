import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta
from jose import JWTError, jwt

from ..config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_OAUTH_REDIRECT, SECRET_KEY
from ..database import SessionLocal, get_db
from ..models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_USER_EMAILS_URL = "https://api.github.com/user/emails"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def create_access_token(data: dict, expires_delta=None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.get("/github/login")
async def github_login():
    """Redirect user to GitHub OAuth authorization"""
    github_auth_params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_OAUTH_REDIRECT,
        "scope": "user:email",
        "state": "random-state-string"  # TODO: use random state for CSRF protection
    }
    
    # Build auth URL
    auth_url = f"{GITHUB_AUTH_URL}?"
    auth_url += "&".join([f"{k}={v}" for k, v in github_auth_params.items()])
    
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            json={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code, # GitHub ticket
                "redirect_uri": GITHUB_OAUTH_REDIRECT
            },
            headers={"Accept": "application/json"}
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token in response")
        
        # Fetch user info from GitHub
        user_response = await client.get(
            GITHUB_USER_URL,
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json"
            }
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info from GitHub")
        
        github_user = user_response.json()
        
        # Fetch emails (to get primary email)
        emails_response = await client.get(
            GITHUB_USER_EMAILS_URL,
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json"
            }
        )
        
        primary_email = github_user.get("email")
        if emails_response.status_code == 200:
            emails = emails_response.json()
            primary = next((e for e in emails if e.get("primary")), None)
            if primary:
                primary_email = primary.get("email")
    
    # Get or create user in database
    user = db.query(User).filter(User.github_id == str(github_user.get("id"))).first()
    
    if user:
        # Update existing user
        user.display_name = github_user.get("name") or github_user.get("login")
        user.email = primary_email or github_user.get("email")
        user.avatar_url = github_user.get("avatar_url")
    else:
        # Create new user
        user = User(
            github_id=str(github_user.get("id")),
            email=primary_email or github_user.get("email"),
            display_name=github_user.get("name") or github_user.get("login"),
            avatar_url=github_user.get("avatar_url")
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    # Create JWT token
    jwt_token = create_access_token(data={"sub": str(user.id)})
    
    # Return token
    return JSONResponse(
        status_code=200,
        content={
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url
            }
        }
    )


@router.get("/me")
async def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user from JWT token (as query param, or use header)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url
    }
