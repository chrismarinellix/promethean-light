"""Authentication API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlmodel import Session
from .database import Database
from .auth_service import AuthService
from .auth_models import User
from .email_service import EmailService


# Request/Response models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Dependencies
def get_db_session():
    db = Database()
    session = db.session()
    try:
        yield session
    finally:
        session.close()


def get_auth_service(session: Session = Depends(get_db_session)) -> AuthService:
    email_service = EmailService()
    return AuthService(session, email_service)


def get_current_user(
    token: Optional[str] = Cookie(None, alias="auth_token"),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user from cookie"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


# Authentication endpoints
@router.post("/register")
async def register(
    request: RegisterRequest,
    req: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    ip_address = req.client.host if req.client else None

    success, message, user = auth_service.register_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        ip_address=ip_address
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "email": user.email if user else None
    }


@router.post("/login")
async def login(
    request: LoginRequest,
    response: Response,
    req: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Log in a user"""
    ip_address = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent")

    success, message, token, user = auth_service.login_user(
        email=request.email,
        password=request.password,
        ip_address=ip_address,
        user_agent=user_agent
    )

    if not success:
        raise HTTPException(status_code=401, detail=message)

    # Set HTTP-only cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True if using HTTPS
        samesite="lax",
        max_age=86400  # 24 hours
    )

    return {
        "success": True,
        "message": message,
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
    }


@router.post("/logout")
async def logout(
    response: Response,
    token: str = Cookie(None, alias="auth_token"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Log out current user"""
    if token:
        auth_service.logout_user(token)

    response.delete_cookie("auth_token")

    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }


@router.get("/verify")
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify email address"""
    success, message = auth_service.verify_email(token)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Resend verification email"""
    success, message = auth_service.resend_verification_email(request.email)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/request-password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset"""
    success, message = auth_service.request_password_reset(request.email)

    return {"success": True, "message": message}


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password with token"""
    success, message = auth_service.reset_password(request.token, request.new_password)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


# Protected endpoint example
@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    """Example protected endpoint"""
    return {
        "message": f"Hello {current_user.full_name}!",
        "email": current_user.email
    }
