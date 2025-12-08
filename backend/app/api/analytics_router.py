from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.db import crud

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.post("/ingest/youtube")
def ingest_youtube_data(user_id: int, db: Session = Depends(get_db)):
    """
    Ingest posts + analytics for YouTube creator
    """
    accounts = crud.get_social_accounts(db, user_id)

    if not accounts:
        return {"error": "No connected social accounts found"}

    # TODO: integrate YouTube API fetch here
    return {"status": "Ingestion started", "accounts": accounts}
