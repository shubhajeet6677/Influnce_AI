import os
import json
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
from sqlalchemy.orm import session
from backend.app.core.database import SessionLocal
from backend.app.db.models import PostAnalytics
from sklearn.model_selection import train_test_split
from sklearn.matrics import mean_absolute_error

MODEL_DIR = "ml/models"
MODEL_PATH = os.path.join(MODEL_DIR, "best_time_predictor.pkl")
COLUMNS_PATH = f"{MODEL_DIR}/best_time_columns.json"

class BestTimePredictor:
    def __init__(self , model_path = MODEL_PATH , columns_path =COLUMNS_PATH , ):
        self.model_path = model_path
        self.columns_path = columns_path
        self.model = None
        self.columns = None
        if os.path.exists(self.model_path) and os.path.exists(self.columns_path):
            self.load_model()

    def load_model(self):
        db: Session = SessionLocal()
        posts = db.query(PostAnalytics).all()
        db.close()

        if not posts:
            raise ValueError("No analytics data found in DB for model training.")
        rows = []
        for p in posts:
            rows.append({
                "posted_at": p.posted_at,
                "likes": p.likes,
                "comments": p.comments,
                "views": p.views,
            })


        df = pd.DataFrame(rows)
        df["posted_at"] = pd.to_datetime(df["posted_at"] , unit="s")
        df["published_hour"] = df["posted_at"].dt.hour
        # engagement score formula (tunable)
        df["engagement"] = df["views"] = df["likes"]* 5 +  df["comments"] * 10

        df.dropna(inplace=True)

        return df

    def train(self):
        df = self.load_data_from_db()

        X = df[[ "published_hour" , "publish_dayofweek" ]]
        X = pd.get_dummies(X , columns=["published_hour" , "publish_dayofweek" ])
        Y = df["engagement"]

        # Save feature columns for prediction alignments
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(COLUMNS_PATH, "w") as f:
            json.dump(list(X.columns), f)

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42 , shuffle=True)

        model = xgb.XGBRegressor(n_estimators=350, max_depth=6, learning_rate=0.05, verbosity=0)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test , preds)

        print("Model Training Completed | MAE:", mae)
        joblib.dump(model, MODEL_PATH)
        self.model = model
        self.columns = list(X.columns)
        return MODEL_PATH

    def predict_best_hour_and_schedule(self):
        if self.model is None:
            raise RuntimeError(f"No model trained for {self.model_path}")

        hourly_scores = []
        for day in range(7):
            for hour in range(24):
                row = pd.DataFrame([[hour,day]], columns=["publish_hour", "publish_dayofweek"])
                row = pd.get_dummies(row, columns=["publish_hour", "publish_dayofweek"])

                for col in self.columns:
                    if col not in row.columns:
                        row[col] = 0

                row = row[self.columns]
                pred = self.model.predict(row)[0]
                hourly_scores.append((day, hour, pred))


        best = max(hourly_scores, key=lambda x: x[2])
        return {
            "best_hour": best[1],
            "best_day": best[0],
            "expected_engagement": round(best[2], 2)
        }
