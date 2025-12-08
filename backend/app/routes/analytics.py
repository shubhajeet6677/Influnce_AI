from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import os

from backend.app.core.database import get_db
from backend.app.db.crud import (
    create_or_update_post,
    insert_post_analytics,
    get_social_accounts
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_STATS_URL = "https://www.googleapis.com/youtube/v3/videos"


def get_user_youtube_token(db: Session, user_id: int):
    accounts = get_social_accounts(db, user_id=user_id)
    for acc in accounts:
        if acc.platform == "youtube":
            return acc.access_token, acc.account_id
    raise HTTPException(status_code=404, detail="No YouTube account linked")

@router.get("/youtube/fetch_posts")
async def fetch_youtube_posts(user_id: int, db: Session = Depends(get_db)):
    access_token, channel_id = get_user_youtube_token(db, user_id)

    params = {
        "part": "snippet",
        "channelId": channel_id,
        "maxResults": 50,
        "order": "date",
        "type": "video"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(
            YOUTUBE_VIDEOS_URL,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"}
        )

    data = res.json()

    if "items" not in data:
        raise HTTPException(status_code=400, detail="Unable to fetch YouTube posts")

    saved_posts = []

    for item in data["items"]:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]

        posted_at = snippet.get("publishedAt")
        posted_at = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))

        post = create_or_update_post(
            db,
            platform_post_id=video_id,
            title=snippet.get("title"),
            caption=snippet.get("description"),
            posted_at=posted_at,
            account_id=user_id
        )

        saved_posts.append(post.id)

    return {"message": "Posts fetched successfully", "count": len(saved_posts)}


@router.get("/youtube/fetch_analytics")
async def fetch_youtube_analytics(user_id: int, db: Session = Depends(get_db)):
    access_token, _ = get_user_youtube_token(db, user_id)

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{YOUTUBE_STATS_URL}?part=statistics,snippet&myRating=like",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    data = res.json()

    if "items" not in data:
        raise HTTPException(status_code=400, detail="Unable to fetch analytics")

    for item in data["items"]:
        video_id = item["id"]
        stats = item.get("statistics", {})

        # Extract values safely
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        shares = 0  # YouTube does not provide share count
        dislikes = 0

        # Save analytics in DB
        insert_post_analytics(
            db=db,
            post_id=video_id,
            likes=likes,
            dislikes=dislikes,
            comments=comments,
            shares=shares,
            views=views
        )

    return {"message": "Analytics saved successfully", "total": len(data["items"])}
