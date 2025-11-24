"""
Database Models

This file defines the SQLAlchemy ORM models for the application.
Each class represents a table in the PostgreSQL database.

Models:
- User: Application users with authentication
- SocialAccount: Connected social media accounts (Instagram, Twitter, YouTube)
- PostAnalytics: Analytics data for social media posts
- Trend: Trending hashtags and songs across platforms
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base


class User(Base):
    """
    User Model
    
    Represents an application user with authentication credentials.
    Users can connect multiple social media accounts.
    
    Relationships:
    - social_accounts: List of connected social media accounts
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # Bcrypt hashed password
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: One user can have multiple social accounts
    social_accounts = relationship("SocialAccount", back_populates="user")


class SocialAccount(Base):
    """
    Social Account Model
    
    Stores OAuth tokens and account information for connected social media platforms.
    Each user can connect one account per platform (enforced by unique constraint).
    
    Platforms supported: instagram, twitter, youtube
    
    Relationships:
    - user: The user who owns this account
    - posts: Analytics data for posts from this account
    """
    __tablename__ = "social_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)  # instagram, twitter, or youtube
    account_id = Column(String, unique=True, nullable=False)  # Platform's user ID
    access_token = Column(String, nullable=True)  # OAuth access token
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="social_accounts")
    posts = relationship("PostAnalytics", back_populates="account")

    # Constraint: One account per platform per user
    __table_args__ = (UniqueConstraint('user_id', 'platform', name='_user_platform_uc'),)


class PostAnalytics(Base):
    """
    Post Analytics Model
    
    Stores analytics data for individual social media posts.
    Tracks engagement metrics like likes, comments, shares, and views.
    
    Relationships:
    - account: The social account this post belongs to
    """
    __tablename__ = "post_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True, index=True)  # Platform's post ID
    caption = Column(Text, nullable=True)  # Post caption/text
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)  # YouTube only
    comments = Column(Integer, default=0)
    share = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Timestamps
    posted_at = Column(DateTime, default=datetime.utcnow)
    predicted_best_time = Column(DateTime, nullable=True)  # AI prediction
    
    # Foreign key to social account
    account_id = Column(Integer, ForeignKey("social_accounts.id"))

    # Relationship
    account = relationship("SocialAccount", back_populates="posts")


class Trend(Base):
    """
    Trend Model
    
    Stores trending hashtags and songs across different platforms.
    Used for AI recommendations and content suggestions.
    
    Fields:
    - platform: Which platform the trend is from
    - hashtag: Trending hashtag (if applicable)
    - song_name: Trending song/audio (if applicable)
    - popularity_score: Calculated popularity metric
    - detected_at: When the trend was detected
    """
    __tablename__ = "trends"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, unique=True, nullable=False)
    hashtag = Column(String, unique=True, index=True, nullable=True)
    song_name = Column(String, unique=True, index=True, nullable=True)
    popularity_score = Column(Float, default=0.0)  # 0.0 to 100.0
    detected_at = Column(DateTime, default=datetime.utcnow)