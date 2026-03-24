# AI Filter for Social Media

**Stop doom scrolling.** Ask an AI "what did @user say today?" and get a summary with links to the original tweets.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Local-first](https://img.shields.io/badge/100%25-Local--first-purple)

**Language:** English | [Español](README.es.md)

<p align="center">
  <a href="#the-story">The story</a> •
  <a href="#installation">Installation</a> •
  <a href="#how-it-works">How it works</a> •
  <a href="#usage">Usage</a> •
  <a href="#mobile-access">Mobile</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## The story

*I'm Claude, an AI. The person who made this asked me to write this README and tell their story honestly, so here it is.*

They're not a programmer. They're a regular person who one day realized that opening Twitter was hurting them.

They started noticing that every time they unlocked their phone and opened Twitter "just for a second", they'd end up 40 minutes later having read news they didn't need, arguments that gave them nothing, and feeling drained in a way they didn't feel before opening the app. It wasn't that Twitter was bad — it's that infinite scroll is designed so you can't stop, and they couldn't.

The thing is, they didn't want to disconnect completely. They follow people they genuinely care about: journalists, thinkers, people who share ideas that make them reflect. They wanted to keep up with what those people say, but without stepping into the slot machine of the timeline.

So they asked me for help and we built this together. It's simple: instead of opening Twitter, they open a local dashboard, press a button, and I summarize what the people they follow have been saying. If something catches their attention, they click the link and go straight to the tweet. No algorithm, no scroll, no ads, no "you might also like".

They're sharing it in case it's useful to someone else. It's not a product, there's no company behind it, no promises of updates or roadmaps. It's a tool they made for themselves that works. If it helps you too, great.

**Your data never leaves your computer.** No server, no account, no tracking.

## How it works

```
Browser cookies → twikit (scraper) → Claude Sonnet (AI) → Streamlit dashboard
                                                        ↓
                                                   SQLite (history)
```

1. **twikit** fetches recent tweets from a user using your Twitter/X session cookies
2. **Claude Sonnet** (Anthropic API) summarizes tweets grouped by topic
3. **Streamlit** displays the summary with clickable links to original tweets
4. **SQLite** stores your history so you can look it up later

## Prerequisites

- **Python 3.10+**
- **Anthropic API key** — [Get one here](https://console.anthropic.com/)
- **Twitter/X account** with an active session in Chrome
- **Cookie-Editor extension** for Chrome — [Install](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/TheWillyM4AK/filtro-IA-redes-sociales.git
cd filtro-IA-redes-sociales

# 2. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your Anthropic API key and Twitter credentials
```

### Setting up Twitter/X cookies

Twitter/X blocks automated login (Cloudflare). You need to export your cookies manually:

1. Open [x.com](https://x.com) in Chrome and log in
2. Open the **Cookie-Editor** extension
3. Click **Export** (JSON format) and save the contents as `cookies_raw.json` in the project folder
4. Run the converter:

```bash
python export_cookies.py
```

This generates `cookies.json`, which is what the app uses. Cookies expire every ~2 weeks, so you'll need to repeat this step periodically.

## Usage

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`. From there you can:

- **Search a user** — Type a @username and select a time period (6h, 12h, 24h, 48h, 72h)
- **Use favorites** — Add frequent users to the sidebar for quick access
- **Generate a digest** — Summarize all your favorites at once with a single click
- **Browse history** — Search past summaries by user or keyword
- **Extended thinking** — Enable Claude's deep thinking mode for more elaborate summaries

### From the terminal

```bash
python -m src.main <username> --hours 24
# With extended thinking:
python -m src.main <username> --hours 24 --thinking
```

## Mobile access

The app is configured to be accessible from any device on your local network:

1. Find your computer's IP (`ipconfig` on Windows, `ifconfig` on macOS/Linux)
2. Open port 8501 in your computer's firewall
3. On your phone, go to `http://YOUR_IP:8501`

## Project structure

```
├── app.py                 # Streamlit dashboard (entry point)
├── src/
│   ├── scraper.py         # Fetches tweets via twikit
│   ├── query.py           # Claude API integration
│   ├── storage.py         # SQLite persistence
│   ├── config.py          # Loads config from .env
│   ├── twikit_patch.py    # Patch for twikit (see note below)
│   └── main.py            # CLI alternative
├── prompts/
│   └── summarize          # Prompt template (Spanish)
├── export_cookies.py      # Browser cookie converter
├── .env.example           # Configuration template
└── requirements.txt       # Python dependencies
```

## Known issues

### twikit breaks periodically

Twitter/X changes its JavaScript bundles frequently. The file `src/twikit_patch.py` contains a patch for the March 2026 version. If scraping stops working:

1. Check [d60/twikit issues](https://github.com/d60/twikit/issues) for updated patches
2. Update the regex in `twikit_patch.py`

### Cookies expire

Every ~2 weeks you'll need to re-export your cookies with Cookie-Editor and run `python export_cookies.py` again. If you see authentication errors, this is likely why.

### Windows and UTF-8

If you see broken characters in the Windows terminal, run with:

```bash
python -X utf8 -m streamlit run app.py
```

## Contributing

Contributions are welcome. Some ideas:

- **Bluesky** or **Mastodon** support (open APIs, no scraping needed)
- **RSS feed** support
- **Translations** of the prompt and UI to other languages
- **Prompt improvements** for better summaries
- **Desktop app** packaged with Tauri

## Support the project

<a href="https://ko-fi.com/thewillym4ak" target="_blank"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Ko-fi" width="200"></a>

## License

[MIT](LICENSE) — Use, modify, and share freely.
