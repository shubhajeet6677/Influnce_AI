# OAuth Setup Guide for InfluenceAI

This guide will help you set up OAuth authentication for Instagram, Twitter/X, and YouTube.

## Prerequisites

1. Docker Desktop running
2. PostgreSQL and Redis containers running (`docker-compose up -d`)
3. Python dependencies installed (`pip install -r backend/requirements.txt`)

## Platform Setup

### 1. Instagram OAuth Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or use an existing one
3. Add Instagram Basic Display product
4. Configure OAuth redirect URI: `http://localhost:8000/auth/instagram/callback`
5. Copy your **App ID** and **App Secret**
6. Update `.env`:
   ```
   INSTAGRAM_APP_ID=your_app_id_here
   INSTAGRAM_SECRET=your_app_secret_here
   ```

### 2. Twitter/X OAuth Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Enable OAuth 2.0
4. Add callback URL: `http://localhost:8000/auth/twitter/callback`
5. Copy your **Client ID** and **Client Secret**
6. Update `.env`:
   ```
   TWITTER_CLIENT_ID=your_client_id_here
   TWITTER_CLIENT_SECRET=your_client_secret_here
   ```

### 3. YouTube (Google) OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3 and YouTube Analytics API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Add authorized redirect URI: `http://localhost:8000/auth/youtube/callback`
6. Copy your **Client ID** and **Client Secret**
7. Update `.env`:
   ```
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```

## Running the Application

1. Start Docker containers:
   ```bash
   docker-compose up -d
   ```

2. Run database migrations:
   ```bash
   python -m alembic upgrade head
   ```

3. Start the FastAPI server:
   ```bash
   python -m uvicorn backend.app.main:app --reload
   ```

4. Access the API documentation: http://localhost:8000/docs

## API Endpoints

### Authentication

- **POST** `/auth/register` - Register a new user
- **POST** `/auth/login` - Login user

### OAuth Connections

- **GET** `/auth/instagram` - Get Instagram OAuth URL
- **GET** `/auth/instagram/callback` - Instagram OAuth callback
- **GET** `/auth/twitter` - Get Twitter OAuth URL
- **GET** `/auth/twitter/callback` - Twitter OAuth callback
- **GET** `/auth/youtube` - Get YouTube OAuth URL
- **GET** `/auth/youtube/callback` - YouTube OAuth callback

### Analytics

- **GET** `/social/instagram/insights?user_id=1` - Get Instagram posts and metrics
- **GET** `/social/instagram/profile?user_id=1` - Get Instagram profile info
- **GET** `/social/twitter/tweets?user_id=1` - Get Twitter tweets and metrics
- **GET** `/social/twitter/profile?user_id=1` - Get Twitter profile info
- **GET** `/social/youtube/videos?user_id=1` - Get YouTube videos
- **GET** `/social/youtube/analytics?user_id=1` - Get YouTube channel analytics
- **GET** `/social/connected-accounts?user_id=1` - Get all connected accounts

## OAuth Flow

1. User registers/logs in to get a JWT token
2. User initiates OAuth by calling `/auth/{platform}` endpoint
3. User is redirected to the platform's authorization page
4. After authorization, platform redirects to `/auth/{platform}/callback`
5. Backend exchanges code for access token and stores it in database
6. User can now fetch analytics using the `/social/*` endpoints

## Database Schema

The application uses the following tables:

- **users** - User accounts
- **social_accounts** - Connected social media accounts with access tokens
- **post_analytics** - Analytics data for posts
- **trends** - Trending hashtags and songs

## Security Notes

- Never commit `.env` file to version control
- Use strong, random values for `JWT_SECRET` in production
- Enable HTTPS in production
- Implement proper user authentication middleware
- Add rate limiting to prevent API abuse
- Regularly rotate OAuth tokens

## Next Steps

1. Implement proper user authentication middleware
2. Add frontend for OAuth flow
3. Create ETL pipelines to fetch and store analytics data
4. Build analytics dashboard
5. Implement ML models for predictions
