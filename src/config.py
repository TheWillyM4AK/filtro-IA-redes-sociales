"""Configuration loader. Reads .env and exposes settings."""

import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")

# Comma-separated list of favorite Twitter handles (without @)
FAVORITE_USERS = [
    u.strip() for u in os.getenv("FAVORITE_USERS", "").split(",") if u.strip()
]

# Claude model settings
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 4096
