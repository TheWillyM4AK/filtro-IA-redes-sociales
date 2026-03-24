"""Twitter/X data fetcher using twikit.

Replaces the fragile Playwright-based scraper from ai-sanity
with twikit's cookie-based API access.
"""

import os
import json
from datetime import datetime, timedelta, timezone

import src.twikit_patch  # noqa: F401 — must be imported before twikit
from twikit import Client

COOKIES_PATH = os.path.join(os.path.dirname(__file__), "..", "cookies.json")


async def create_client() -> Client:
    """Create and authenticate a twikit client.

    First tries to load saved cookies. If no cookies exist,
    logs in with credentials and saves cookies for next time.
    """
    client = Client("en-US")

    if os.path.isfile(COOKIES_PATH):
        client.load_cookies(COOKIES_PATH)
    else:
        from src.config import TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD
        await client.login(
            auth_info_1=TWITTER_USERNAME,
            auth_info_2=TWITTER_EMAIL,
            password=TWITTER_PASSWORD,
        )
        client.save_cookies(COOKIES_PATH)

    return client


async def get_user_tweets(username: str, hours: int = 24, max_tweets: int = 50) -> list[dict]:
    """Fetch recent tweets from a specific user.

    Args:
        username: Twitter handle without @.
        hours: How far back to look (default 24h).
        max_tweets: Maximum tweets to fetch.

    Returns:
        List of tweet dicts with keys: username, text, tweet_id,
        created_at, likes, retweets, url.
    """
    client = await create_client()

    # Find the user
    user = await client.get_user_by_screen_name(username)
    if not user:
        return []

    # Fetch their tweets
    raw_tweets = await user.get_tweets("Tweets", count=max_tweets)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    tweets = []

    for tweet in raw_tweets:
        created_at = tweet.created_at_datetime
        if created_at and created_at < cutoff:
            continue

        tweets.append({
            "username": username,
            "text": tweet.full_text or tweet.text or "",
            "tweet_id": tweet.id,
            "created_at": str(created_at) if created_at else "",
            "likes": tweet.favorite_count or 0,
            "retweets": tweet.retweet_count or 0,
            "url": f"https://x.com/{username}/status/{tweet.id}",
        })

    return tweets
