from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_token = Column(Text, nullable=True)      # short-lived token
    refresh_token = Column(Text, nullable=True)     # long-lived, used to refresh access_token
    platform = Column(String, nullable=False)       # 'youtube' / 'instagram'
    expires_at = Column(DateTime, nullable=True)    # absolute expiry time (optional)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="tokens")


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    account_id = Column(String, nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="social_accounts")
    posts = relationship("Post", back_populates="social_account")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, index=True)
    title = Column(String)
    caption = Column(Text)
    media_type = Column(String)
    posted_at = Column(DateTime, nullable=False)
    account_id = Column(Integer, ForeignKey("social_accounts.id"))

    social_account = relationship("SocialAccount", back_populates="posts")
    analytics = relationship("PostAnalytics", back_populates="post")


class PostAnalytics(Base):
    __tablename__ = "post_analytics"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    snapshot_at = Column(DateTime, default=datetime.utcnow)
    predicted_best_time = Column(DateTime, nullable=True)

    post = relationship("Post", back_populates="analytics")


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    hashtag = Column(String, index=True)
    song_name = Column(String, index=True)
    popularity_score = Column(Float, default=0.0)
    detected_at = Column(DateTime, default=datetime.utcnow)
