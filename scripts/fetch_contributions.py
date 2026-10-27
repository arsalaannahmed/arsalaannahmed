"""Fetch Arsalaan's public contribution calendar, no token needed.

Source: https://github.com/users/arsalaannahmed/contributions
(the same public fragment GitHub's own profile page uses).
Writes data/contributions.json with day cells and totals.
Adapted from the pattern in Avi Vashishta's animated README guide.
"""
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "arsalaannahmed"
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = Path(__file__).resolve().parent.parent

resp = requests.get(URL, timeout=30, headers={"User-Agent": "profile-readme-refresh"})
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

days = []
for el in soup.select("[data-date]"):
    level = el.get("data-level")
    count = el.get("data-count")
    if level is None:
        continue
    try:
        days.append({
            "date": el["data-date"],
            "level": int(level),
            "count": int(count) if count is not None else 0,
        })
    except (ValueError, KeyError):
        continue

# Fallback: contribution graph sometimes renders as <rect> elements.
if not days:
    for el in soup.select("rect[data-date]"):
        try:
            days.append({
                "date": el["data-date"],
                "level": int(el.get("data-level", 0)),
                "count": int(el.get("data-count", 0)),
            })
        except ValueError:
            continue

total_text = soup.get_text()
m = re.search(r"(\d[\d,]*)\s+contributions in the last year", total_text)
total = int(m.group(1).replace(",", "")) if m else sum(d["count"] for d in days)

out = {"username": USERNAME, "total_last_year": total, "days": days}
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "contributions.json").write_text(json.dumps(out, indent=2))
print(f"Wrote {len(days)} days, total {total}")
