"""Convert browser-exported cookies to twikit format.

Usage:
    1. Install "Cookie-Editor" Chrome extension
    2. Go to x.com, click Cookie-Editor, click "Export" → "Export as JSON"
    3. Save to cookies_raw.json in this project folder
    4. Run: python export_cookies.py
"""

import json
import os

RAW_PATH = "cookies_raw.json"
OUTPUT_PATH = "cookies.json"

if not os.path.isfile(RAW_PATH):
    print(f"Error: {RAW_PATH} not found.")
    print("Export cookies from Cookie-Editor extension and save them here.")
    exit(1)

with open(RAW_PATH, "r", encoding="utf-8") as f:
    browser_cookies = json.load(f)

# Convert from [{name, value, domain, ...}] to {name: value}
twikit_cookies = {}
for c in browser_cookies:
    domain = c.get("domain", "")
    if "x.com" in domain or "twitter.com" in domain:
        twikit_cookies[c["name"]] = c["value"]

# Check for essential cookies
essential = ["auth_token", "ct0"]
missing = [k for k in essential if k not in twikit_cookies]
if missing:
    print(f"Warning: missing essential cookies: {missing}")
    print("Make sure you're logged into x.com before exporting.")
else:
    print(f"Found {len(twikit_cookies)} cookies ({', '.join(essential)} present)")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(twikit_cookies, f, indent=2)

print(f"Saved to {OUTPUT_PATH}")
