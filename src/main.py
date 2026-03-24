"""Main entry point — CLI for quick testing.

Usage:
    python -m src.main <username> [--hours 24] [--thinking]
"""

import asyncio
import argparse

from src.scraper import get_user_tweets
from src.query import summarize_user_tweets, format_tweets_for_prompt


async def main():
    parser = argparse.ArgumentParser(description="AI filter for Twitter/X")
    parser.add_argument("username", help="Twitter handle without @")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back (default: 24)")
    parser.add_argument("--thinking", action="store_true", help="Enable extended thinking")
    args = parser.parse_args()

    print(f"Fetching tweets from @{args.username} (last {args.hours}h)...")
    tweets = await get_user_tweets(args.username, hours=args.hours)
    print(f"Found {len(tweets)} tweets.\n")

    if not tweets:
        print(f"No recent tweets from @{args.username}.")
        return

    print("Generating summary with Claude...\n")
    summary = summarize_user_tweets(args.username, tweets, use_thinking=args.thinking)
    print(summary)


if __name__ == "__main__":
    asyncio.run(main())
