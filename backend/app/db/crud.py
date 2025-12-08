from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db import models


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Fetch a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Fetch user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Fetch user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def list_users(db: Session) -> List[models.User]:
    """Return all users"""
    return db.query(models.User).all()


def create_user(db: Session, username: str, email: str, hashed_password: str) -> models.User:
    """
    Create and store new user
    """
    user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except Exception as e:
        db.rollback()
        raise e
