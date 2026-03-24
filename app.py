"""Streamlit dashboard — AI filter for Twitter/X."""

import asyncio
import json
import os
import streamlit as st
from src.scraper import get_user_tweets
from src.query import summarize_user_tweets
from src.config import FAVORITE_USERS
from src.storage import save_summary, get_history

FAVORITES_PATH = os.path.join(os.path.dirname(__file__), "favorites.json")


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


st.set_page_config(page_title="Filtro IA - Twitter/X", page_icon="🧠", layout="wide")

st.title("🧠 Filtro IA para Twitter/X")
st.caption("Consume Twitter sin doom scrolling. Resúmenes con IA, no algoritmos.")

# --- Initialize session state ---
if "favorites" not in st.session_state:
    st.session_state["favorites"] = load_favorites()

# --- Sidebar: favorite users ---
st.sidebar.header("Usuarios favoritos")

fav_hours = st.sidebar.selectbox(
    "Periodo",
    [6, 12, 24, 48, 72],
    index=2,
    format_func=lambda h: f"Últimas {h}h",
    key="fav_hours",
)

for user in st.session_state["favorites"]:
    if st.sidebar.button(f"@{user}", key=f"fav_{user}", use_container_width=True):
        st.session_state["username"] = user
        st.session_state["hours_override"] = fav_hours
        st.session_state["run_query"] = True
        st.rerun()

# Remove a favorite (separate section to avoid clutter)
with st.sidebar.expander("Quitar usuario"):
    for user in st.session_state["favorites"]:
        if st.button(f"Quitar @{user}", key=f"del_{user}", use_container_width=True):
            st.session_state["favorites"].remove(user)
            save_favorites(st.session_state["favorites"])
            st.rerun()

# Add new favorite
st.sidebar.divider()
new_fav = st.sidebar.text_input("Añadir usuario", placeholder="ej: elonmusk")
if st.sidebar.button("Añadir", use_container_width=True) and new_fav:
    new_fav = new_fav.strip().lstrip("@")
    if new_fav and new_fav not in st.session_state["favorites"]:
        st.session_state["favorites"].append(new_fav)
        save_favorites(st.session_state["favorites"])
        st.rerun()

# Digest button
st.sidebar.divider()
st.sidebar.subheader("Digest")
digest_hours = st.sidebar.selectbox("Periodo del digest", [6, 12, 24, 48], index=2, format_func=lambda h: f"Últimas {h}h", key="digest_hours")
if st.sidebar.button("Generar digest de todos", use_container_width=True, type="primary"):
    st.session_state["run_digest"] = True
    st.session_state["digest_hours_val"] = digest_hours
    st.rerun()

# --- Main area ---
col1, col2 = st.columns([3, 1])
with col1:
    username = st.text_input(
        "Usuario de Twitter/X (sin @)",
        value=st.session_state.get("username", ""),
        placeholder="ej: elonmusk",
    )
with col2:
    # Use sidebar period if coming from a favorite button click
    default_idx = 2
    if "hours_override" in st.session_state:
        override = st.session_state.pop("hours_override")
        options = [6, 12, 24, 48, 72]
        default_idx = options.index(override) if override in options else 2
    hours = st.selectbox("Periodo", [6, 12, 24, 48, 72], index=default_idx, format_func=lambda h: f"Últimas {h}h")

use_thinking = st.checkbox("Activar pensamiento extendido (más lento, más caro, más profundo)")

run = st.button("Resumir", type="primary", use_container_width=True) or st.session_state.get("run_query", False)

# Clear the run_query flag
if "run_query" in st.session_state:
    del st.session_state["run_query"]

if run and username:
    username = username.strip().lstrip("@")

    with st.status(f"Obteniendo tweets de @{username}...", expanded=True) as status:
        st.write(f"Buscando tweets de las últimas {hours} horas...")
        tweets = asyncio.run(get_user_tweets(username, hours=hours))
        st.write(f"Encontrados **{len(tweets)}** tweets.")

        if not tweets:
            status.update(label=f"No hay tweets recientes de @{username}", state="complete")
            st.info(f"@{username} no ha publicado nada en las últimas {hours} horas.")
        else:
            st.write("Generando resumen con Claude Sonnet...")
            summary = summarize_user_tweets(username, tweets, use_thinking=use_thinking)
            save_summary(username, summary, tweets, hours)
            status.update(label=f"Resumen de @{username} ({len(tweets)} tweets)", state="complete")

    if tweets:
        st.markdown(summary)

        # Expandable: raw tweets
        with st.expander(f"Ver los {len(tweets)} tweets originales"):
            sort_order = st.radio(
                "Ordenar por",
                ["Más recientes", "Más relevantes"],
                horizontal=True,
            )
            if sort_order == "Más recientes":
                sorted_tweets = sorted(tweets, key=lambda t: t["created_at"], reverse=True)
            else:
                sorted_tweets = sorted(tweets, key=lambda t: t["likes"] + t["retweets"], reverse=True)

            for t in sorted_tweets:
                relevance = t['likes'] + t['retweets']
                st.markdown(
                    f"**@{t['username']}** · {t['created_at'][:16]} · "
                    f"❤️ {t['likes']} · 🔁 {t['retweets']} · "
                    f"📊 {relevance} relevancia\n\n"
                    f"{t['text']}\n\n"
                    f"[Ver en Twitter/X]({t['url']})\n\n---"
                )
elif run:
    st.warning("Escribe un nombre de usuario.")

# --- Digest: all favorites at once ---
if st.session_state.get("run_digest"):
    del st.session_state["run_digest"]
    digest_h = st.session_state.get("digest_hours_val", 24)
    favorites = st.session_state.get("favorites", [])

    if not favorites:
        st.warning("No tienes usuarios favoritos. Añade algunos en el sidebar.")
    else:
        st.header(f"Digest de {len(favorites)} usuarios (últimas {digest_h}h)")
        progress = st.progress(0, text="Iniciando digest...")

        for i, user in enumerate(favorites):
            progress.progress((i) / len(favorites), text=f"Obteniendo tweets de @{user}...")
            tweets = asyncio.run(get_user_tweets(user, hours=digest_h))

            if not tweets:
                st.info(f"@{user} — sin tweets recientes.")
                continue

            progress.progress((i + 0.5) / len(favorites), text=f"Resumiendo @{user} ({len(tweets)} tweets)...")
            summary = summarize_user_tweets(user, tweets)
            save_summary(user, summary, tweets, digest_h)

            with st.expander(f"@{user} — {len(tweets)} tweets", expanded=True):
                st.markdown(summary)

        progress.progress(1.0, text="Digest completado.")

# --- History section ---
st.divider()
st.header("Historial de resúmenes")

search = st.text_input("Buscar en el historial", placeholder="usuario o palabra clave...")
history = get_history(search=search)

if not history:
    st.caption("No hay resúmenes guardados todavía." if not search else "Sin resultados para esa búsqueda.")
else:
    for entry in history:
        timestamp = entry["created_at"][:16].replace("T", " ")
        with st.expander(f"@{entry['username']} · {timestamp} · {entry['tweet_count']} tweets · {entry['hours']}h"):
            st.markdown(entry["summary"])
            tweets_data = json.loads(entry["tweets_json"])
            st.caption(f"{len(tweets_data)} tweets originales")
            for t in tweets_data[:5]:
                st.markdown(
                    f"> **@{t['username']}** · {t.get('created_at', '')[:16]} · "
                    f"[Ver tweet]({t['url']})\n> {t['text'][:200]}{'...' if len(t['text']) > 200 else ''}"
                )
