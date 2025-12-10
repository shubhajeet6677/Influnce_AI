from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.db import crud
from backend.app.services.youtube_ingest import ingest_youtube
from backend.app.services.instagram_ingest import ingest_instagram
from datetime import datetime
from collections import defaultdict

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.post("/ingest/youtube")
async def ingest_youtube_data(user_id: int, db: Session = Depends(get_db)):
    accounts = crud.get_social_accounts(db, user_id)

    yt_accounts = [acc for acc in accounts if acc.platform.lower() == "youtube"]
    if not yt_accounts:
        raise HTTPException(status_code=404, detail="No connected YouTube accounts found")

    for acc in yt_accounts:
        await ingest_youtube(db=db, account=acc)

    return {"status": "completed", "platform": "youtube", "ingested_accounts": len(yt_accounts)}


@router.post("/ingest/instagram")
async def ingest_instagram_data(user_id: int, db: Session = Depends(get_db)):
    accounts = crud.get_social_accounts(db, user_id)

    ig_accounts = [acc for acc in accounts if acc.platform.lower() == "instagram"]
    if not ig_accounts:
        raise HTTPException(status_code=404, detail="No connected Instagram accounts found")

    for acc in ig_accounts:
        await ingest_instagram(db=db, account=acc)

    return {"status": "completed", "platform": "instagram", "ingested_accounts": len(ig_accounts)}


@router.post("/ingest/all")
async def ingest_all_platforms(user_id: int, db: Session = Depends(get_db)):
    accounts = crud.get_social_accounts(db, user_id)

    if not accounts:
        raise HTTPException(status_code=404, detail="No connected social accounts found")

    for acc in accounts:
        if acc.platform.lower() == "youtube":
            await ingest_youtube(db=db, account=acc)
        elif acc.platform.lower() == "instagram":
            await ingest_instagram(db=db, account=acc)

    return {"status": "completed", "platforms_synced": list(set([acc.platform for acc in accounts]))}

@router.get("/overview")
def analytics_overview(user_id: int, db: Session = Depends(get_db)):
    posts = crud.get_posts_with_analytics_joined(db, user_id)

    if not posts:
        return {"message": "No analytics data available yet"}

    total_posts = len(posts)
    total_views = sum(p.analytics.views for p in posts)
    total_likes = sum(p.analytics.likes for p in posts)
    total_comments = sum(p.analytics.comments for p in posts)

    top_post = max(posts, key=lambda p: p.analytics.views)

    return {
        "total_posts": total_posts,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "top_post": {
            "caption": top_post.caption,
            "views": top_post.analytics.views,
            "likes": top_post.analytics.likes,
            "posted_at": top_post.posted_at,
        }
    }


@router.get("/timeseries")
def engagement_timeseries(user_id: int, db: Session = Depends(get_db)):
    posts = crud.get_posts_with_analytics_joined(db, user_id)

    if not posts:
        return {"message": "No analytics history available yet"}

    timeseries = [
        {
            "posted_at": p.posted_at,
            "views": p.analytics.views,
            "likes": p.analytics.likes,
            "comments": p.analytics.comments,
            "engagement_score": (p.analytics.likes + p.analytics.comments) / max(p.analytics.views, 1)
        }
        for p in sorted(posts, key=lambda x: x.posted_at)
    ]

    return {"timeline": timeseries}


@router.get("/performance")
def performance_insights(user_id: int, db: Session = Depends(get_db)):
    """
    Returns performance insights (best day, best hour, top post, trends)
    """
    posts = crud.get_posts_with_analytics_joined(db, user_id)

    if not posts:
        raise HTTPException(status_code=404, detail="No analytics found")

    from collections import defaultdict
    import numpy as np

    day_engagement = defaultdict(list)
    hour_engagement = defaultdict(list)

    top_post = None
    max_engagement_score = -1

    for post in posts:
        analytics = post.analytics

        # Compute engagement score
        engagement = (analytics.likes + analytics.comments) / max(analytics.views, 1)

        # Detect top-performing post
        if engagement > max_engagement_score:
            max_engagement_score = engagement
            top_post = post

        # Convert timestamp correctly
        dt = post.posted_at
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))

        day = dt.strftime("%A")
        hour = dt.hour

        day_engagement[day].append(engagement)
        hour_engagement[hour].append(engagement)

    # Best day based on average engagement
    best_day = max(day_engagement.items(), key=lambda x: np.mean(x[1]))[0]

    # Best hour based on average engagement
    best_hour = max(hour_engagement.items(), key=lambda x: np.mean(x[1]))[0]

    # Build weekday trend list
    weekday_trend = [
        {"day": day, "avg_engagement": float(np.mean(vals))}
        for day, vals in sorted(day_engagement.items())
    ]

    # Build hourly trend list
    hourly_trend = [
        {"hour": hour, "avg_engagement": float(np.mean(vals))}
        for hour, vals in sorted(hour_engagement.items())
    ]

    avg_eng = float(
        sum((p.analytics.likes + p.analytics.comments) / max(p.analytics.views, 1)
            for p in posts) / len(posts)
    )

    return {
        "best_day": best_day,
        "best_hour": f"{best_hour}:00",
        "top_post": {
            "caption": top_post.caption,
            "views": top_post.analytics.views,
            "likes": top_post.analytics.likes,
            "comments": top_post.analytics.comments,
            "posted_at": str(top_post.posted_at),
        },
        "weekday_trend": weekday_trend,
        "hourly_trend": hourly_trend,
        "avg_engagement": avg_eng
    }
