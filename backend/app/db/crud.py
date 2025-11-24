from sqlalchemy.orm import Session
from backend.app.db import models

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_social_account(db: Session, user_id: int, platform: str):
    return db.query(models.SocialAccount).filter(
        models.SocialAccount.user_id == user_id,
        models.SocialAccount.platform == platform
    ).first()

def create_or_update_social_account(db: Session, user_id: int, platform: str, account_id: str, access_token: str):
    account = get_social_account(db, user_id, platform)
    if account:
        account.access_token = access_token
        account.account_id = account_id # Update account_id just in case
    else:
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