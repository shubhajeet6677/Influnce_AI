import httpx
from sqlalchemy.orm import Session
from backend.app.db import crud, models

INSTAGRAM_MEDIA_API = "https://graph.instagram.com/me/media"
INSTAGRAM_INSIGHTS_API = "https://graph.instagram.com/{media_id}/insights"


async def fetch_instagram_posts(access_token: str):
    params = {
        "fields": "id,caption,media_type,timestamp",
        "access_token": access_token
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(INSTAGRAM_MEDIA_API, params=params)
        return res.json()


async def fetch_instagram_insights(media_id: str, access_token: str):
    params = {
        "metric": "likes,comments,impressions,reach,saved,shares",
        "access_token": access_token
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(INSTAGRAM_INSIGHTS_API.format(media_id=media_id), params=params)
        return res.json()


async def ingest_instagram(db: Session, account: models.SocialAccount):
    posts = await fetch_instagram_posts(account.access_token)

    if "data" not in posts:
        return {"error": "Failed to fetch Instagram posts"}

    for item in posts["data"]:
        post = crud.create_post(
            db=db,
            account_id=account.id,
            caption=item.get("caption", ""),
            posted_at=item.get("timestamp")
        )

        insights = await fetch_instagram_insights(item["id"], account.access_token)
        metrics = {i["name"]: int(i["values"][0]["value"]) for i in insights.get("data", [])}

        crud.create_post_analytics(
            db=db,
            post_id=post.id,
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            views=metrics.get("impressions", 0),
            shares=metrics.get("shares", 0)
        )

    return {"success": True, "message": "Instagram ingestion complete"}
