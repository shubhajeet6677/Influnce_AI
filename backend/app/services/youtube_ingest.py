import httpx
from sqlalchemy.orm import Session
from backend.app.db import crud, models

YOUTUBE_VIDEO_API = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_ANALYTICS_API = "https://www.googleapis.com/youtube/v3/videos"


async def fetch_youtube_posts(access_token: str, channel_id: str):
    """
    Fetch recent YouTube videos for a channel
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": 10,
            "order": "date"
        }

        res = await client.get(YOUTUBE_VIDEO_API, params=params, headers=headers)
        return res.json()


async def fetch_youtube_analytics(access_token: str, video_ids: str):
    """
    Fetch analytics like views, likes, comments
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        params = {
            "part": "statistics",
            "id": video_ids
        }

        res = await client.get(YOUTUBE_ANALYTICS_API, params=params, headers=headers)
        return res.json()


async def ingest_youtube(db: Session, account: models.SocialAccount):
    """
    Ingest posts + analytics for a YouTube creator
    """
    posts = await fetch_youtube_posts(account.access_token, account.account_id)

    if "items" not in posts:
        return {"error": "Failed to retrieve posts from YouTube"}

    for item in posts["items"]:
        video_id = item["id"].get("videoId")
        if not video_id:
            continue

        caption = item["snippet"]["title"]
        posted_at = item["snippet"]["publishedAt"]

        # Save post
        post = crud.create_post(
            db=db,
            account_id=account.id,
            caption=caption,
            posted_at=posted_at
        )

        # Fetch analytics
        analytics = await fetch_youtube_analytics(account.access_token, video_id)
        stats = analytics["items"][0]["statistics"]

        crud.create_post_analytics(
            db=db,
            post_id=post.id,
            likes=int(stats.get("likeCount", 0)),
            comments=int(stats.get("commentCount", 0)),
            shares=0,  # YouTube does not expose share count
            views=int(stats.get("viewCount", 0))
        )

    return {"success": True, "message": "YouTube ingestion completed"}
