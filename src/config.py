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

# Data directory for persistent files (data.db, cookies.json, favorites.json).
# Defaults to the project root. Set to "/data" in Docker for volume mount.
_PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.getenv("DATA_DIR", _PROJECT_ROOT)

# App password for remote access. If empty, no authentication required.
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
