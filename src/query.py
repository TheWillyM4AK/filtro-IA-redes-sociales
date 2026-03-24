"""Claude API integration for summarizing tweets.

Adapted from joelchan/ai-sanity — fixed the double-prompt bug,
switched to configurable model, added extended thinking support.
"""

import os
import anthropic
from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Path to the prompts directory
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _read_prompt(name: str) -> str:
    """Read a prompt template from the prompts/ directory."""
    path = os.path.join(PROMPTS_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def call_claude(prompt: str, model: str = CLAUDE_MODEL, use_thinking: bool = False) -> str:
    """Send a prompt to Claude and return the text response.

    Args:
        prompt: The user message to send.
        model: Claude model ID.
        use_thinking: If True, enables extended thinking (higher cost).
    """
    kwargs = {
        "model": model,
        "max_tokens": CLAUDE_MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }

    if use_thinking:
        kwargs["temperature"] = 1  # required for extended thinking
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": 5000}
        kwargs["max_tokens"] = 16000  # must be > budget_tokens

    response = client.messages.create(**kwargs)

    # With thinking enabled, extract the text block (skip thinking blocks)
    for block in response.content:
        if block.type == "text":
            return block.text

    return ""


def format_tweets_for_prompt(tweets: list[dict]) -> str:
    """Format a list of tweet dicts into a string for Claude.

    Each tweet dict should have: username, text, tweet_id, created_at.
    """
    lines = []
    for i, tweet in enumerate(tweets, 1):
        username = tweet.get("username", "unknown")
        tweet_id = tweet.get("tweet_id", "")
        text = tweet.get("text", "")
        lines.append(f"Tweet {i} (@{username}/{tweet_id}): {text}")
    return "\n".join(lines)


def chunk_tweets(tweets: list[dict], max_words: int = 2000) -> list[list[dict]]:
    """Split tweets into chunks that fit within token limits.

    Adapted from ai-sanity's chunking logic.
    """
    chunks = []
    current_chunk = []
    current_words = 0

    for tweet in tweets:
        tweet_words = len(tweet.get("text", "").split())
        if current_words + tweet_words > max_words and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_words = 0
        current_chunk.append(tweet)
        current_words += tweet_words

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def summarize_user_tweets(username: str, tweets: list[dict], use_thinking: bool = False, lang: str = "es") -> str:
    """Generate a summary of a user's recent tweets.

    Args:
        username: The Twitter handle (without @).
        tweets: List of tweet dicts from that user.
        use_thinking: Enable extended thinking for complex analysis.
        lang: Language code ("es" or "en") for the prompt template.

    Returns:
        A summary string with tweet citations.
    """
    if not tweets:
        if lang == "en":
            return f"No recent tweets found from @{username}."
        return f"No se encontraron tweets recientes de @{username}."

    prompt_name = "summarize" if lang == "es" else "summarize_en"
    prompt_template = _read_prompt(prompt_name)
    formatted_tweets = format_tweets_for_prompt(tweets)
    prompt = prompt_template.replace("{username}", username).replace("{tweets}", formatted_tweets)

    return call_claude(prompt, use_thinking=use_thinking)
