"""Authentication service for user management"""

import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from passlib.context import CryptContext
from sqlmodel import Session, select
from .auth_models import User, UserSession, LoginAttempt
from .email_service import EmailService


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, store this securely
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class AuthService:
    """Handle user authentication and management"""

    def __init__(self, session: Session, email_service: Optional[EmailService] = None):
        self.session = session
        self.email_service = email_service or EmailService()

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: int, email: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def is_valid_email_domain(self, email: str) -> bool:
        """Check if email domain is allowed"""
        allowed_domains = ["vysusgroup.com"]
        domain = email.split("@")[-1].lower()
        return domain in allowed_domains

    def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user

        Returns: (success, message, user)
        """
        # Validate email domain
        if not self.is_valid_email_domain(email):
            return False, "Only @vysusgroup.com email addresses are allowed", None

        # Check if user already exists
        existing_user = self.session.exec(
            select(User).where(User.email == email)
        ).first()

        if existing_user:
            return False, "Email already registered", None

        # Create user
        verification_token = secrets.token_urlsafe(32)
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=self.hash_password(password),
            is_active=True,  # Auto-approve
            is_admin=False,
            email_verified=False,
            verification_token=verification_token,
            verification_token_expires=datetime.utcnow() + timedelta(hours=24)
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        # Send verification email
        self.email_service.send_verification_email(
            to_email=user.email,
            full_name=user.full_name,
            verification_token=verification_token
        )

        # Notify admin
        self.email_service.notify_admin_new_user(
            user_email=user.email,
            full_name=user.full_name
        )

        return True, "Registration successful! Please check your email to verify your account.", user

    def verify_email(self, token: str) -> Tuple[bool, str]:
        """Verify user email with token"""
        user = self.session.exec(
            select(User).where(User.verification_token == token)
        ).first()

        if not user:
            return False, "Invalid verification token"

        if user.email_verified:
            return True, "Email already verified. You can log in."

        if user.verification_token_expires and datetime.utcnow() > user.verification_token_expires:
            return False, "Verification token expired. Please request a new one."

        # Verify email
        user.email_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        self.session.add(user)
        self.session.commit()

        # Send welcome email
        self.email_service.send_welcome_email(
            to_email=user.email,
            full_name=user.full_name
        )

        return True, "Email verified successfully! You can now log in."

    def login_user(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str], Optional[User]]:
        """
        Log in a user

        Returns: (success, message, token, user)
        """
        # Find user
        user = self.session.exec(
            select(User).where(User.email == email.lower())
        ).first()

        # Log attempt
        attempt = LoginAttempt(
            email=email.lower(),
            success=False,
            ip_address=ip_address
        )

        if not user or not self.verify_password(password, user.hashed_password):
            self.session.add(attempt)
            self.session.commit()
            return False, "Invalid email or password", None, None

        if not user.is_active:
            self.session.add(attempt)
            self.session.commit()
            return False, "Account is not active. Please contact administrator.", None, None

        if not user.email_verified:
            self.session.add(attempt)
            self.session.commit()
            return False, "Please verify your email before logging in. Check your inbox.", None, None

        # Successful login
        attempt.success = True
        self.session.add(attempt)

        # Update last login
        user.last_login = datetime.utcnow()
        self.session.add(user)

        # Create session token
        token = self.create_access_token(user.id, user.email)

        # Store session
        session = UserSession(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(session)
        self.session.commit()

        return True, "Login successful", token, user

    def logout_user(self, token: str) -> bool:
        """Log out user by invalidating token"""
        session = self.session.exec(
            select(UserSession).where(UserSession.token == token)
        ).first()

        if session:
            self.session.delete(session)
            self.session.commit()
            return True

        return False

    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from JWT token"""
        # Verify token
        payload = self.verify_token(token)
        if not payload:
            return None

        # Check if session exists
        session = self.session.exec(
            select(UserSession).where(UserSession.token == token)
        ).first()

        if not session:
            return None

        if datetime.utcnow() > session.expires_at:
            self.session.delete(session)
            self.session.commit()
            return None

        # Get user
        user = self.session.get(User, int(payload["sub"]))
        if not user or not user.is_active or not user.email_verified:
            return None

        return user

    def request_password_reset(self, email: str) -> Tuple[bool, str]:
        """Request password reset"""
        user = self.session.exec(
            select(User).where(User.email == email.lower())
        ).first()

        if not user:
            # Don't reveal if email exists
            return True, "If that email is registered, you will receive a password reset link."

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        self.session.add(user)
        self.session.commit()

        # Send reset email
        self.email_service.send_password_reset_email(
            to_email=user.email,
            full_name=user.full_name,
            reset_token=reset_token
        )

        return True, "If that email is registered, you will receive a password reset link."

    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """Reset password with token"""
        user = self.session.exec(
            select(User).where(User.reset_token == token)
        ).first()

        if not user:
            return False, "Invalid reset token"

        if user.reset_token_expires and datetime.utcnow() > user.reset_token_expires:
            return False, "Reset token expired. Please request a new one."

        # Reset password
        user.hashed_password = self.hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        self.session.add(user)

        # Invalidate all sessions
        sessions = self.session.exec(
            select(UserSession).where(UserSession.user_id == user.id)
        ).all()
        for session in sessions:
            self.session.delete(session)

        self.session.commit()

        return True, "Password reset successfully. You can now log in with your new password."

    def resend_verification_email(self, email: str) -> Tuple[bool, str]:
        """Resend verification email"""
        user = self.session.exec(
            select(User).where(User.email == email.lower())
        ).first()

        if not user:
            return False, "Email not found"

        if user.email_verified:
            return False, "Email already verified"

        # Generate new token
        verification_token = secrets.token_urlsafe(32)
        user.verification_token = verification_token
        user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        self.session.add(user)
        self.session.commit()

        # Send email
        self.email_service.send_verification_email(
            to_email=user.email,
            full_name=user.full_name,
            verification_token=verification_token
        )

        return True, "Verification email sent. Please check your inbox."
