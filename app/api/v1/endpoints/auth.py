from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import secrets

from app.db.session import get_db
from app.models.user import User
from app.models.reset_token import PasswordResetToken
from app.schemas.auth_schemas import UserRegister, TokenResponse, UserOut
from app.core.auth import (
    hash_password, verify_password,
    create_access_token, get_current_user, require_admin
)
from pydantic import BaseModel

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201, summary="Register a new user")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    is_first = db.query(User).count() == 0
    role = "admin" if is_first else payload.role

    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password[:72]),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse, summary="Login with JSON credentials")
def login_json(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "full_name": user.full_name, "email": user.email, "role": user.role}
    )


@router.post("/login/form", response_model=TokenResponse, summary="Login with form data")
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "full_name": user.full_name, "email": user.email, "role": user.role}
    )


@router.get("/me", response_model=UserOut, summary="Get current logged-in user")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=List[UserOut], summary="List all users (admin only)")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).all()


@router.patch("/users/{user_id}/deactivate", response_model=UserOut, summary="Deactivate a user (admin only)")
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


# ── Forgot Password ───────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password", summary="Request password reset email")
async def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    from app.services.email_service import send_reset_email
    from app.core.config import settings

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        return {"message": "If that email exists, a reset link has been sent."}

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).update({"is_used": True})

    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    db.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires))
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password.html?token={token}"
    await send_reset_email(user.email, user.full_name or user.username, reset_link)

    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password", summary="Reset password with token")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == payload.token,
        PasswordResetToken.is_used == False,
    ).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    if datetime.utcnow() > record.expires_at.replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Reset link has expired. Please request a new one.")

    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    user = db.query(User).filter(User.id == record.user_id).first()
    user.hashed_password = hash_password(payload.new_password[:72])
    record.is_used = True
    db.commit()

    return {"message": "Password reset successfully. You can now log in."}