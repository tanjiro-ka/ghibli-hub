import httpx
import secrets
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import RedirectResponse, JSONResponse

from ..config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_OAUTH_REDIRECT
from ..database import get_db
from ..models.user import User
from sqlalchemy.orm import Session
from .session import create_access_token, create_refresh_token, decode_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_USER_EMAILS_URL = "https://api.github.com/user/emails"


@router.get("/github/login")
async def github_login():
    """Redirect user to GitHub OAuth authorization"""
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    github_auth_params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_OAUTH_REDIRECT,
        "scope": "user:email",
        "state": state
    }
    
    # Build auth URL
    auth_url = f"{GITHUB_AUTH_URL}?"
    auth_url += "&".join([f"{k}={v}" for k, v in github_auth_params.items()])
    
    # Note: In production, store state in session/cache (Redis) to validate in callback
    # For now, we generate it but don't validate it (acceptable for MVP)
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    # Note: In production, validate state against session/cache to prevent CSRF
    # For now, we accept any state (acceptable for MVP but not for production)
    if not state:
        raise HTTPException(status_code=400, detail="Missing state parameter")
    
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
    
    # Create JWT tokens (access + refresh)
    jwt_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Return tokens (frontend should store the access token and refresh token securely)
    return JSONResponse(
        status_code=200,
        content={
            "access_token": jwt_token,
            "refresh_token": refresh_token,
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
async def me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user (uses Authorization: Bearer <token>)"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "avatar_url": current_user.avatar_url
    }
    
    
@router.post("/refresh")
async def refresh_access_token(request_body: dict = Body(...), db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    refresh_token = request_body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh_token in request body")
    
    try:
        payload = decode_token(refresh_token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access = create_access_token({"sub": str(user.id)})
    return JSONResponse(status_code=200, content={"access_token": new_access, "token_type": "bearer"})
