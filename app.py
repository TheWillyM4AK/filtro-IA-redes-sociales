"""Streamlit dashboard — AI filter for Twitter/X."""

import asyncio
import json
import os
import streamlit as st
from src.scraper import get_user_tweets, COOKIES_PATH
from src.query import summarize_user_tweets
from src.config import FAVORITE_USERS, DATA_DIR, APP_PASSWORD
from src.storage import save_summary, get_history
from src.i18n import get_strings

FAVORITES_PATH = os.path.join(DATA_DIR, "favorites.json")


def load_favorites() -> list[str]:
    """Load favorites from JSON file, falling back to .env config."""
    if os.path.isfile(FAVORITES_PATH):
        with open(FAVORITES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return list(FAVORITE_USERS)


def save_favorites(favorites: list[str]):
    """Persist favorites to JSON file."""
    with open(FAVORITES_PATH, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


def process_cookie_text(raw_json: str) -> tuple[bool, str, int]:
    """Convert pasted Cookie-Editor JSON to twikit format.

    Returns (success, message, cookie_count).
    """
    try:
        browser_cookies = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return False, str(e), 0

    twikit_cookies = {}
    for c in browser_cookies:
        domain = c.get("domain", "")
        if "x.com" in domain or "twitter.com" in domain:
            twikit_cookies[c["name"]] = c["value"]

    essential = ["auth_token", "ct0"]
    missing = [k for k in essential if k not in twikit_cookies]
    if missing:
        return False, ", ".join(missing), 0

    with open(COOKIES_PATH, "w", encoding="utf-8") as f:
        json.dump(twikit_cookies, f, indent=2)

    return True, "", len(twikit_cookies)


st.set_page_config(page_title="AI Filter - Twitter/X", page_icon="🧠", layout="wide")

# --- Mobile-friendly CSS ---
st.markdown("""
<style>
@media (max-width: 768px) {
    .stButton > button {
        min-height: 48px;
        font-size: 1rem;
    }
    .stTextInput > div > div > input {
        font-size: 1rem;
        min-height: 44px;
    }
    .stSelectbox > div > div {
        min-height: 44px;
    }
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Language selector (must come before any other UI) ---
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

lang_options = {"English": "en", "Español": "es"}
lang_label = st.sidebar.selectbox(
    "🌐",
    list(lang_options.keys()),
    index=list(lang_options.values()).index(st.session_state["lang"]),
    key="lang_select",
)
st.session_state["lang"] = lang_options[lang_label]
t = get_strings(st.session_state["lang"])

# --- Authentication gate ---
if APP_PASSWORD:
    if not st.session_state.get("authenticated"):
        st.title(f"🧠 {t['login_title']}")
        password = st.text_input(t["login_password"], type="password")
        if st.button(t["login_button"], type="primary", use_container_width=True):
            if password == APP_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error(t["login_error"])
        st.stop()

st.title(f"🧠 {t['title']}")
st.caption(t["caption"])

# --- Initialize session state ---
if "favorites" not in st.session_state:
    st.session_state["favorites"] = load_favorites()

# --- Sidebar: favorite users ---
st.sidebar.header(t["favorites_header"])

fav_hours = st.sidebar.selectbox(
    t["period"],
    [6, 12, 24, 48, 72],
    index=2,
    format_func=lambda h: t["last_hours"].format(h=h),
    key="fav_hours",
)

for user in st.session_state["favorites"]:
    if st.sidebar.button(f"@{user}", key=f"fav_{user}", use_container_width=True):
        st.session_state["username"] = user
        st.session_state["hours_override"] = fav_hours
        st.session_state["run_query"] = True
        st.rerun()

# Remove a favorite (separate section to avoid clutter)
with st.sidebar.expander(t["remove_user"]):
    for user in st.session_state["favorites"]:
        if st.button(t["remove_prefix"].format(user=user), key=f"del_{user}", use_container_width=True):
            st.session_state["favorites"].remove(user)
            save_favorites(st.session_state["favorites"])
            st.rerun()

# Add new favorite
st.sidebar.divider()
new_fav = st.sidebar.text_input(t["add_user"], placeholder=t["add_user_placeholder"])
if st.sidebar.button(t["add_button"], use_container_width=True) and new_fav:
    new_fav = new_fav.strip().lstrip("@")
    if new_fav and new_fav not in st.session_state["favorites"]:
        st.session_state["favorites"].append(new_fav)
        save_favorites(st.session_state["favorites"])
        st.rerun()

# Digest button
st.sidebar.divider()
st.sidebar.subheader(t["digest"])
digest_hours = st.sidebar.selectbox(t["digest_period"], [6, 12, 24, 48], index=2, format_func=lambda h: t["last_hours"].format(h=h), key="digest_hours")
if st.sidebar.button(t["digest_button"], use_container_width=True, type="primary"):
    st.session_state["run_digest"] = True
    st.session_state["digest_hours_val"] = digest_hours
    st.rerun()

# --- Sidebar: Cookie paste ---
st.sidebar.divider()
with st.sidebar.expander(t["cookies_header"]):
    cookies_exist = os.path.isfile(COOKIES_PATH)
    status_text = t["cookies_ok"] if cookies_exist else t["cookies_not_found"]
    st.caption(t["cookies_status"].format(status=status_text))
    st.caption(t["cookies_info"])
    cookie_json = st.text_area(
        t["cookies_paste"],
        height=100,
        placeholder=t["cookies_paste_placeholder"],
        key="cookie_paste",
    )
    if st.button(t["cookies_save_button"], key="save_cookies", use_container_width=True):
        if cookie_json.strip():
            ok, msg, count = process_cookie_text(cookie_json)
            if ok:
                st.success(t["cookies_success"].format(count=count))
            elif msg and "," in msg:
                st.warning(t["cookies_missing"].format(missing=msg))
            else:
                st.error(t["cookies_error"].format(error=msg))
        else:
            st.warning(t["cookies_empty"])

# --- Sidebar: Logout ---
if APP_PASSWORD:
    st.sidebar.divider()
    if st.sidebar.button(t["logout_button"], use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# --- Main area ---
col1, col2 = st.columns([3, 1])
with col1:
    username = st.text_input(
        t["username_input"],
        value=st.session_state.get("username", ""),
        placeholder=t["username_placeholder"],
    )
with col2:
    # Use sidebar period if coming from a favorite button click
    default_idx = 2
    if "hours_override" in st.session_state:
        override = st.session_state.pop("hours_override")
        options = [6, 12, 24, 48, 72]
        default_idx = options.index(override) if override in options else 2
    hours = st.selectbox(t["period"], [6, 12, 24, 48, 72], index=default_idx, format_func=lambda h: t["last_hours"].format(h=h))

use_thinking = st.checkbox(t["thinking_checkbox"])

lang = st.session_state["lang"]
run = st.button(t["summarize_button"], type="primary", use_container_width=True) or st.session_state.get("run_query", False)

# Clear the run_query flag
if "run_query" in st.session_state:
    del st.session_state["run_query"]

if run and username:
    username = username.strip().lstrip("@")

    with st.status(t["fetching_tweets"].format(user=username), expanded=True) as status:
        st.write(t["searching_tweets"].format(hours=hours))
        tweets = asyncio.run(get_user_tweets(username, hours=hours))
        st.write(t["found_tweets"].format(count=len(tweets)))

        if not tweets:
            status.update(label=t["no_recent_tweets"].format(user=username), state="complete")
            st.info(t["no_tweets_info"].format(user=username, hours=hours))
        else:
            st.write(t["generating_summary"])
            summary = summarize_user_tweets(username, tweets, use_thinking=use_thinking, lang=lang)
            save_summary(username, summary, tweets, hours)
            status.update(label=t["summary_label"].format(user=username, count=len(tweets)), state="complete")

    if tweets:
        st.markdown(summary)

        # Expandable: raw tweets
        with st.expander(t["view_original"].format(count=len(tweets))):
            sort_order = st.radio(
                t["sort_by"],
                [t["most_recent"], t["most_relevant"]],
                horizontal=True,
            )
            if sort_order == t["most_recent"]:
                sorted_tweets = sorted(tweets, key=lambda tw: tw["created_at"], reverse=True)
            else:
                sorted_tweets = sorted(tweets, key=lambda tw: tw["likes"] + tw["retweets"], reverse=True)

            for tw in sorted_tweets:
                relevance = tw['likes'] + tw['retweets']
                st.markdown(
                    f"**@{tw['username']}** · {tw['created_at'][:16]} · "
                    f"❤️ {tw['likes']} · 🔁 {tw['retweets']} · "
                    f"📊 {relevance} {t['relevance']}\n\n"
                    f"{tw['text']}\n\n"
                    f"[{t['view_on_twitter']}]({tw['url']})\n\n---"
                )
elif run:
    st.warning(t["enter_username"])

# --- Digest: all favorites at once ---
if st.session_state.get("run_digest"):
    del st.session_state["run_digest"]
    digest_h = st.session_state.get("digest_hours_val", 24)
    favorites = st.session_state.get("favorites", [])

    if not favorites:
        st.warning(t["no_favorites"])
    else:
        st.header(t["digest_header"].format(count=len(favorites), hours=digest_h))
        progress = st.progress(0, text=t["starting_digest"])

        for i, user in enumerate(favorites):
            progress.progress((i) / len(favorites), text=t["digest_fetching"].format(user=user))
            tweets = asyncio.run(get_user_tweets(user, hours=digest_h))

            if not tweets:
                st.info(t["digest_no_tweets"].format(user=user))
                continue

            progress.progress((i + 0.5) / len(favorites), text=t["digest_summarizing"].format(user=user, count=len(tweets)))
            summary = summarize_user_tweets(user, tweets, lang=lang)
            save_summary(user, summary, tweets, digest_h)

            with st.expander(t["digest_user_label"].format(user=user, count=len(tweets)), expanded=True):
                st.markdown(summary)

        progress.progress(1.0, text=t["digest_done"])

# --- History section ---
st.divider()
st.header(t["history_header"])

search = st.text_input(t["history_search"], placeholder=t["history_search_placeholder"])
history = get_history(search=search)

if not history:
    st.caption(t["history_empty"] if not search else t["history_no_results"])
else:
    for entry in history:
        timestamp = entry["created_at"][:16].replace("T", " ")
        with st.expander(f"@{entry['username']} · {timestamp} · {entry['tweet_count']} tweets · {entry['hours']}h"):
            st.markdown(entry["summary"])
            tweets_data = json.loads(entry["tweets_json"])
            st.caption(t["original_tweets"].format(count=len(tweets_data)))
            for tw in tweets_data[:5]:
                st.markdown(
                    f"> **@{tw['username']}** · {tw.get('created_at', '')[:16]} · "
                    f"[{t['view_tweet']}]({tw['url']})\n> {tw['text'][:200]}{'...' if len(tw['text']) > 200 else ''}"
                )
