"""Render data/contributions.json as an animated 53x7 heatmap SVG.

Palette and diagonal reveal follow the animated-README pattern:
GitHub-ish green ramp, slide-down once on load, then frozen.
"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

data = json.loads((ROOT / "data" / "contributions.json").read_text())
by_date = {d["date"]: d for d in data.get("days", [])}
total = data.get("total_last_year", sum(d["count"] for d in data.get("days", [])))

# Build a 53-week grid ending this week (Sunday-first columns like GitHub).
today = date.today()
# GitHub weeks start Sunday; find the Sunday of this week.
start_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
grid_start = start_sunday - timedelta(weeks=52)

cell, gap = 12, 3
cols, rows = 53, 7
w = cols * (cell + gap) + 40
h = rows * (cell + gap) + 70

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="190" viewBox="0 0 {w} {h}">',
    '<style>.cell{animation: drop .5s forwards; opacity:0} '
    "@keyframes drop{from{transform:translateY(-6px);opacity:0} "
    "to{transform:translateY(0);opacity:1}}</style>",
    f'<rect width="{w}" height="{h}" rx="14" fill="#0d1117" stroke="#30363d"/>',
]
for c in range(cols):
    for r in range(rows):
        day = grid_start + timedelta(weeks=c, days=r)
        level = by_date.get(day.isoformat(), {}).get("level", 0)
        level = max(0, min(5, int(level)))
        x = 20 + c * (cell + gap)
        y = 16 + r * (cell + gap)
        delay = round((c + r) * 0.02, 2)
        parts.append(
            f'<rect class="cell" style="animation-delay:{delay}s" '
            f'x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
            f'fill="{PALETTE[level]}"><title>{day.isoformat()}</title></rect>'
        )
parts.append(f'<text x="20" y="{h-28}" font-family="monospace" font-size="13" fill="#8b949e">Less</text>')
for i, col in enumerate(PALETTE[:5]):
    parts.append(f'<rect x="{70 + i * 16}" y="{h-40}" width="12" height="12" rx="3" fill="{col}"/>')
parts.append(f'<text x="160" y="{h-28}" font-family="monospace" font-size="13" fill="#8b949e">More</text>')
parts.append(
    f'<text x="20" y="{h-10}" font-family="monospace" font-size="13" fill="#e6edf3">'
    f'{total} contributions in the last year — refreshed daily.</text>'
)
parts.append("</svg>")
(ROOT / "contrib-heatmap.svg").write_text("\n".join(parts))
print(f"Wrote contrib-heatmap.svg, total {total}")
