"""
Database CRUD Operations

This module contains all database operations (Create, Read, Update, Delete).
These functions are used by the API routes to interact with the database.

Functions are organized by model:
- User operations
- Social Account operations
"""

from sqlalchemy.orm import Session
from backend.app.db import models


# ==================== User Operations ====================

def get_user(db: Session, user_id: int):
    """
    Get a user by ID
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        User object or None if not found
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """
    Get a user by email address
    
    Args:
        db: Database session
        email: User's email
        
    Returns:
        User object or None if not found
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, username: str, email: str, hashed_password: str):
    """
    Create a new user
    
    Args:
        db: Database session
        username: Desired username
        email: User's email
        hashed_password: Bcrypt hashed password
        
    Returns:
        Created User object
    """
    user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==================== Social Account Operations ====================

def get_social_account(db: Session, user_id: int, platform: str):
    """
    Get a user's social account for a specific platform
    
    Args:
        db: Database session
        user_id: User's ID
        platform: Platform name (instagram, twitter, youtube)
        
    Returns:
        SocialAccount object or None if not found
    """
    return db.query(models.SocialAccount).filter(
        models.SocialAccount.user_id == user_id,
        models.SocialAccount.platform == platform
    ).first()


def create_or_update_social_account(
    db: Session, 
    user_id: int, 
    platform: str, 
    account_id: str, 
    access_token: str
):
    """
    Create a new social account or update existing one
    
    This function handles both initial OAuth connection and token refresh.
    If an account already exists for this user+platform, it updates the token.
    Otherwise, it creates a new account record.
    
    Args:
        db: Database session
        user_id: User's ID
        platform: Platform name (instagram, twitter, youtube)
        account_id: Platform's user ID
        access_token: OAuth access token
        
    Returns:
        Created or updated SocialAccount object
    """
    # Check if account already exists
    account = get_social_account(db, user_id, platform)
    
    if account:
        # Update existing account
        account.access_token = access_token
        account.account_id = account_id  # Update account_id in case it changed
    else:
        # Create new account
        account = models.SocialAccount(
            user_id=user_id,
            platform=platform,
            account_id=account_id,
            access_token=access_token
        )
        db.add(account)
    
    db.commit()
    db.refresh(account)
    return account