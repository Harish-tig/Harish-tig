#!/usr/bin/env python3
"""
Generate an animated GitHub contribution heatmap with a continuous purple snake game.
Based on dahan8473/snake-and-commits algorithm.

Theme:
  - Contribution cells: Green GitHub-style tones (#161b22, #0e4429, #006d32, #26a641, #39d353)
  - Snake: Continuous Purple (#f3e8ff head, #d8b4fe -> #a855f7 -> #7e22ce body ramp)
  - Terminal frame: Dark GitHub background (#0d1117) with terminal buttons and title

Supports:
  - Token-based GraphQL query (in GitHub Actions via GH_TOKEN / GITHUB_TOKEN)
  - Fallback to data/contributions.json or public scraper for local generation
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
from bisect import bisect_right
from collections import deque
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(HERE, "..", "assets", "svg", "snake-contributions.svg")
DATA_PATH = os.path.join(HERE, "..", "data", "contributions.json")

CELL, GAP = 11, 3
PITCH = CELL + GAP
MX, MTOP, MBOT = 20, 36, 28
STEPS_PER_SEC = 10
PAUSE_STEPS = 26
BASE_LEN = 3

LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
         "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Custom theme: Green contribution cells with a Vibrant Purple Snake
THEME = dict(
    levels=["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    snake="#a855f7",
    head="#f3e8ff",
    ramp=[(1, "#f3e8ff"), (4, "#d8b4fe"), (10, "#a855f7"), (21, "#7e22ce")],
    text="#7d8590",
    frame_bg="#0d1117",
    frame_border="#30363d",
)


def get_token():
    for k in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    try:
        res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return ""


def fetch_weeks_graphql(user, tok):
    now = datetime.now(timezone.utc)
    frm = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = """
    query($login:String!,$from:DateTime!){user(login:$login){contributionsCollection(from:$from){
      contributionCalendar{weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"login": user, "from": frm}}).encode(),
        headers={"Authorization": f"Bearer {tok}", "User-Agent": user},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def fetch_weeks_from_json(user):
    """Fallback to local data/contributions.json if available, or scrape."""
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            days = data.get("days", [])
            if days:
                # Group days into weeks (starting on Sunday)
                weeks = []
                cur_week = []
                for d in days:
                    # date parsing
                    dt = datetime.strptime(d["date"], "%Y-%m-%d")
                    cnt = d.get("count", 0)
                    lvl = "NONE" if cnt == 0 else ("FIRST_QUARTILE" if cnt <= 3 else ("SECOND_QUARTILE" if cnt <= 6 else ("THIRD_QUARTILE" if cnt <= 12 else "FOURTH_QUARTILE")))
                    day_info = {
                        "date": d["date"],
                        "contributionCount": cnt,
                        "contributionLevel": lvl
                    }
                    cur_week.append(day_info)
                    if dt.weekday() == 5 or len(cur_week) == 7: # Saturday or full week
                        weeks.append({"contributionDays": cur_week})
                        cur_week = []
                if cur_week:
                    weeks.append({"contributionDays": cur_week})
                return weeks
        except Exception as e:
            print(f"Warning: could not parse local {DATA_PATH}: {e}", file=sys.stderr)
            
    # Try public scraper fallback
    url = f"https://github-contributions-api.jogruber.de/v4/{user}?y=last"
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            raw = json.loads(r.read().decode())
            contribs = raw.get("contributions", [])
            weeks = []
            cur_week = []
            for d in contribs:
                cnt = d.get("count", 0)
                level_idx = d.get("level", 0)
                lvl_names = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
                cur_week.append({
                    "date": d["date"],
                    "contributionCount": cnt,
                    "contributionLevel": lvl_names[min(4, level_idx)]
                })
                if len(cur_week) == 7:
                    weeks.append({"contributionDays": cur_week})
                    cur_week = []
            if cur_week:
                weeks.append({"contributionDays": cur_week})
            return weeks
    except Exception as e:
        raise RuntimeError(f"Failed to fetch contributions data: {e}")


def solve(grid, cap=999):
    """BFS Snake solver from dahan8473/snake-and-commits."""
    ncols = len(grid)

    def neighbors(cr):
        c, r = cr
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nc, nr = c + dc, r + dr
            if 0 <= nc < ncols and 0 <= nr < len(grid[nc]):
                yield (nc, nr)

    def bfs(start_, goal, blocked):
        if start_ == goal:
            return [start_]
        qq, seen = deque([(start_, [start_])]), {start_}
        while qq:
            cur, path = qq.popleft()
            for nb in neighbors(cur):
                if nb in seen or (nb in blocked and nb != goal):
                    continue
                if nb == goal:
                    return path + [nb]
                seen.add(nb)
                qq.append((nb, path + [nb]))
        return None

    remaining = {(c, r) for c in range(ncols) for r in range(len(grid[c])) if grid[c][r] > 0}
    start = min(remaining, key=lambda cr: cr[0] * 10 + abs(cr[1] - 3)) if remaining else (0, 3)
    body = deque([start])
    occupied = {start}
    route, eats, growth = [start], [], []

    def allowed():
        return BASE_LEN + len(growth)

    def eat(cell):
        remaining.discard(cell)
        eats.append((len(route) - 1, cell))
        if BASE_LEN + len(growth) < cap:
            growth.append(len(route) - 1)

    def step_to(cell):
        route.append(cell)
        body.append(cell)
        occupied.add(cell)
        if cell in remaining:
            eat(cell)
        while len(body) > allowed():
            occupied.discard(body.popleft())

    if start in remaining:
        eat(start)

    def safe(cell):
        if len(body) < 8:
            return True
        grows = cell in remaining
        occ = set(occupied)
        occ.add(cell)
        b0 = body[0]
        if not grows and len(body) + 1 > allowed():
            occ.discard(body[0])
            b0 = body[1] if len(body) > 1 else cell
        return bfs(cell, b0, occ - {b0, cell}) is not None

    stuck = 0
    while remaining and len(route) < 3500:
        head = body[-1]
        blocked = occupied - {head}
        path = None
        for cand in sorted(remaining, key=lambda cr: grid[cr[0]][cr[1]] * 8 +
                           abs(cr[0] - head[0]) + abs(cr[1] - head[1]))[:24]:
            p = bfs(head, cand, blocked)
            if p and len(p) > 1:
                path = p
                break
        if path:
            aborted = False
            for cell in path[1:]:
                if not safe(cell):
                    aborted = True
                    break
                step_to(cell)
            if not aborted:
                stuck = 0
                continue
        stuck += 1
        if stuck > 300:
            break
        head = body[-1]
        blocked = occupied - {head}
        tail = body[0]
        tp = bfs(head, tail, blocked - {tail})
        nxt = None
        if tp and len(tp) > 1 and tp[1] not in occupied and safe(tp[1]):
            nxt = tp[1]
        else:
            free = [nb for nb in neighbors(head) if nb not in occupied]
            pool = [nb for nb in free if safe(nb)] or free
            if pool:
                nxt = max(pool, key=lambda cr: sum(1 for n in neighbors(cr) if n not in occupied))
        if nxt is None:
            break
        step_to(nxt)
    return route, eats, growth, BASE_LEN + len(growth), len(remaining)


def render(grid, counts, months, route, eats, growth, theme):
    t = theme
    ncols = len(grid)
    n = len(route)
    total = n + PAUSE_STEPS
    dur = total / STEPS_PER_SEC

    def pct(s):
        return round(s / total * 100, 3)

    def xy(c, r):
        return MX + c * PITCH, MTOP + r * PITCH

    def length_at(s):
        return BASE_LEN + bisect_right(growth, s)

    intervals, open_iv, prev = {}, {}, set()
    for s in range(n):
        bod = set(route[max(0, s - length_at(s) + 1): s + 1])
        for cell in bod - prev:
            open_iv[cell] = s
        for cell in prev - bod:
            intervals.setdefault(cell, []).append((open_iv.pop(cell), s))
        prev = bod
    for cell, st in open_iv.items():
        intervals.setdefault(cell, []).append((st, total))

    eaten_step = {cell: s for s, cell in eats}
    css, body = [], []
    for c in range(ncols):
        for r in range(len(grid[c])):
            x, y = xy(c, r)
            base = t["levels"][grid[c][r]]
            ivs = intervals.get((c, r), [])
            cls = f"c{c}_{r}"
            body.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{base}"/>')
            if not ivs:
                continue
            stops = [(0.0, base)]
            for a, b in ivs:
                post = base if (c, r) not in eaten_step or eaten_step[(c, r)] > b else t["levels"][0]
                pa = pct(a)
                stops += [(max(pa - .05, 0), None), (pa, t["head"])]
                for age, col in t["ramp"]:
                    if a + age < b:
                        stops.append((pct(a + age), col))
                if b < total:
                    pb = pct(b)
                    stops += [(max(pb - .05, 0), None), (pb, post)]
            frames, last = [], base
            for p, col in stops:
                col = last if col is None else col
                frames.append(f"{p}% {{ fill:{col}; }}")
                last = col
            frames.append(f"100% {{ fill:{last}; }}")
            css.append(f"@keyframes k{cls} {{ {' '.join(frames)} }}\n.{cls} {{ animation:k{cls} {dur:.1f}s linear infinite; }}")

    for c, label in months:
        x, _ = xy(c, 0)
        body.append(f'<text class="lab" x="{x}" y="{MTOP - 7}">{label}</text>')

    lx = MX + ncols * PITCH - GAP - 5 * (CELL + 3) - 55
    ly = MTOP + 7 * PITCH + 9
    body.append(f'<text class="lab" x="{lx-30}" y="{ly+8}">less</text>')
    for i in range(5):
        body.append(f'<rect x="{lx+i*(CELL+3)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{t["levels"][i]}"/>')
    body.append(f'<text class="lab" x="{lx+5*(CELL+3)+6}" y="{ly+8}">more</text>')

    # Commits eaten counter
    total_commits = sum(counts[c][r] for _, (c, r) in eats)
    states, val = [(0, 0)], 0
    for s, (c, r) in eats:
        val += counts[c][r]
        states.append((s, val))
    body.append(f'<text class="lab" x="{MX}" y="{ly+8}">Harish-tig@github: ~$ commits eaten:</text>')
    for i, (s, v) in enumerate(states):
        a = pct(s)
        b = pct(states[i + 1][0]) if i + 1 < len(states) else 100.0
        if b <= a:
            continue
        fr = (f"0% {{ opacity:0; }} {a}% {{ opacity:1; }} {b}% {{ opacity:0; }} 100% {{ opacity:0; }}"
              if b < 100 else f"0% {{ opacity:0; }} {a}% {{ opacity:1; }} 100% {{ opacity:1; }}")
        css.append(f"@keyframes m{i} {{ {fr} }}\n.m{i} {{ animation:m{i} {dur:.1f}s steps(1,end) infinite; }}")
        body.append(f'<text class="cnt m{i}" opacity="0" x="{MX+198}" y="{ly+8}">{v} / {total_commits}</text>')

    w = MX * 2 + ncols * PITCH - GAP
    h = MTOP + 7 * PITCH - GAP + MBOT + 8
    
    mono = "ui-monospace, 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <style>
      .lab {{ font-family:{mono}; font-size:9.5px; fill:{t['text']}; }}
      .cnt {{ font-family:{mono}; font-size:9.5px; fill:{t['snake']}; font-weight:700; }}
      @media (prefers-reduced-motion) {{ * {{ animation:none !important; }} }}
      {chr(10).join(css)}
    </style>
  </defs>
  
  <!-- Outer Window Frame -->
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{t["frame_bg"]}" stroke="{t["frame_border"]}" stroke-width="1.2"/>
  
  <!-- Terminal Titlebar -->
  <line x1="1" y1="26" x2="{w-1}" y2="26" stroke="#21262d" stroke-width="1"/>
  <circle cx="16" cy="13" r="4.5" fill="#ff5f56"/>
  <circle cx="31" cy="13" r="4.5" fill="#ffbd2e"/>
  <circle cx="46" cy="13" r="4.5" fill="#27c93f"/>
  <text class="lab" x="{w // 2}" y="17" text-anchor="middle" fill="#6e7681">Harish-tig@terminal: ~/contributions.sh --snake --purple</text>

  <!-- Heatmap & Snake -->
{chr(10).join('  ' + b for b in body)}
</svg>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate GitHub Purple Snake Contribution SVG.")
    parser.add_argument("--user", default=os.environ.get("GH_PROFILE_USER", "Harish-tig"), help="GitHub username")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output SVG filepath")
    args = parser.parse_args()

    user = args.user
    tok = get_token()
    
    weeks = None
    if tok:
        try:
            print(f"Fetching contribution calendar for {user} using GitHub GraphQL...")
            weeks = fetch_weeks_graphql(user, tok)
        except Exception as e:
            print(f"GraphQL fetch failed: {e}. Trying fallback...", file=sys.stderr)
            
    if not weeks:
        print(f"Fetching contribution calendar for {user} using local/public data...")
        weeks = fetch_weeks_from_json(user)

    grid = [[LEVEL[d["contributionLevel"]] for d in w["contributionDays"]] for w in weeks]
    counts = [[d["contributionCount"] for d in w["contributionDays"]] for w in weeks]
    months, seen = [], None
    for c, w in enumerate(weeks):
        m = int(w["contributionDays"][0]["date"].split("-")[1])
        if m != seen:
            months.append((c, MONTHS[m]))
            seen = m
    if months and months[0][0] == 0 and len(months) > 1 and months[1][0] <= 2:
        months = months[1:]

    print("Solving snake pathfinding (sparse-to-dense)...")
    for cap in (48, 40, 34, 28, 24, 20, 16, 12):
        route, eats, growth, maxlen, left = solve(grid, cap)
        if left == 0:
            break

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    svg_data = render(grid, counts, months, route, eats, growth, THEME)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg_data)
        
    # Also write to contrib-heatmap.svg for backwards compatibility
    legacy_path = os.path.join(HERE, "..", "contrib-heatmap.svg")
    with open(legacy_path, "w", encoding="utf-8") as f:
        f.write(svg_data)

    print(f"Wrote {args.output} ({len(svg_data)} bytes, {len(eats)} commits eaten, max snake len {maxlen})")


if __name__ == "__main__":
    main()
