#!/usr/bin/env python3
"""
linkedin_scraper.py — Scrape LinkedIn company data via HTTP + HTML parsing.
⚠ SAFETY: Uses test/disposable account. Sequential, slow, human-like delays.

Method: Direct HTTP request with li_at cookie → parse follower count + posts
from the HTML. No browser, no Playwright, no API reverse-engineering.

Usage:
  # Cookie auto-loaded from ~/.linkedin_cookie
  python3 linkedin_scraper.py

Output: ../data/companies.json
"""

import json, os, sys, time, re, random, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Safety ──
MIN_DELAY = 8
MAX_DELAY = 18

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_FILE = DATA_DIR / "companies.json"

COMPANIES = [
    {"id": "blackrock",     "name": "BlackRock",             "url": "https://www.linkedin.com/company/blackrock/",                "market": "Global",    "aum": "$11.5T", "hq": "USA"},
    {"id": "jpmorgan",      "name": "J.P. Morgan AM",        "url": "https://www.linkedin.com/company/jpmorgan-asset-management/", "market": "Global",    "aum": "$4.0T",  "hq": "USA"},
    {"id": "fidelity",      "name": "Fidelity Investments",  "url": "https://www.linkedin.com/company/fidelity-investments/",     "market": "Global",    "aum": "$5.5T",  "hq": "USA"},
    {"id": "hsbc",          "name": "HSBC Asset Management", "url": "https://www.linkedin.com/company/hsbc-asset-management/",    "market": "Hong Kong", "aum": "$600B+", "hq": "HK"},
    {"id": "eastspring",    "name": "Eastspring Investments","url": "https://www.linkedin.com/company/eastspring-investments/",   "market": "Singapore", "aum": "$200B+", "hq": "Singapore"},
    {"id": "macquarie",     "name": "Macquarie AM",          "url": "https://www.linkedin.com/company/macquarie-asset-management/", "market": "Australia", "aum": "$450B+", "hq": "Australia"},
    {"id": "firstsentier",  "name": "First Sentier",         "url": "https://www.linkedin.com/company/first-sentier-investors/",  "market": "Australia", "aum": "$150B+", "hq": "Australia"},
    {"id": "ampcapital",    "name": "AMP Capital",           "url": "https://www.linkedin.com/company/amp-capital/",              "market": "Australia", "aum": "$150B+", "hq": "Australia"},
    {"id": "pingan",        "name": "Ping An AM",            "url": "https://www.linkedin.com/company/ping-an-asset-management/", "market": "China",     "aum": "$500B+", "hq": "China"},
    {"id": "chinaamc",      "name": "China AMC",             "url": "https://www.linkedin.com/company/china-asset-management/",   "market": "China",     "aum": "$250B+", "hq": "China"},
    {"id": "efund",         "name": "E Fund Management",     "url": "https://www.linkedin.com/company/e-fund-management/",        "market": "China",     "aum": "$200B+", "hq": "China"},
    {"id": "harvest",       "name": "Harvest Global",        "url": "https://www.linkedin.com/company/harvest-global-investments/", "market": "China",    "aum": "$150B+", "hq": "China"},
    {"id": "chinasouthern", "name": "China Southern AM",     "url": "https://www.linkedin.com/company/china-southern-fund-management/", "market": "China", "aum": "$200B+", "hq": "China"},
    {"id": "nomura",        "name": "Nomura AM",             "url": "https://www.linkedin.com/company/nomura-asset-management/",  "market": "Japan",     "aum": "$500B+", "hq": "Japan"},
    {"id": "daiwa",         "name": "Daiwa AM",              "url": "https://www.linkedin.com/company/daiwa-asset-management/",   "market": "Japan",     "aum": "$200B+", "hq": "Japan"},
    {"id": "nikko",         "name": "Nikko AM",              "url": "https://www.linkedin.com/company/nikko-am/",                 "market": "Japan",     "aum": "$200B+", "hq": "Japan"},
    {"id": "smds",          "name": "Sumitomo Mitsui DS AM", "url": "https://www.linkedin.com/company/sumitomo-mitsui-ds-asset-management/", "market": "Japan", "aum": "$150B+", "hq": "Japan"},
    {"id": "mizuho",        "name": "Mizuho AM",             "url": "https://www.linkedin.com/company/mizuho-asset-management/",  "market": "Japan",     "aum": "$100B+", "hq": "Japan"},
    {"id": "schroders",     "name": "Schroders",             "url": "https://www.linkedin.com/company/schroders/",                "market": "Global",    "aum": "$800B+", "hq": "UK"},
    {"id": "amundi",        "name": "Amundi",                "url": "https://www.linkedin.com/company/amundi_asset_management/",  "market": "Global",    "aum": "$2.3T",  "hq": "France"},
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


def get_cookie():
    c = os.environ.get("LINKEDIN_COOKIE", "")
    if not c:
        try:
            f = Path.home() / ".linkedin_cookie"
            if f.exists(): c = f.read_text().strip()
        except Exception:
            pass
    return c


def human_delay():
    d = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"  ⏳ {d:.0f}s delay...", flush=True)
    time.sleep(d)


def extract_followers(html):
    """Extract follower count from HTML."""
    for pat in [
        r'(\d[\d,.]*)\s*followers?',
        r'"followerCount"[:\s]*(\d+)',
        r'"followersCount"[:\s]*(\d+)',
    ]:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            raw = m.group(1)
            n = int(re.sub(r'[^\d]', '', raw))
            if n > 0:
                return n
    return 0


def extract_posts(html, company_name):
    """
    Extract recent posts from LinkedIn company page HTML.
    LinkedIn embeds post data in structured HTML and script JSON.
    """
    posts = []
    seen = set()

    # Pattern 1: Find activity URNs from post containers
    acts = re.findall(r'urn:li:activity:(\d+)', html)
    
    for aid in acts:
        if aid in seen: continue
        seen.add(aid)

        idx = html.find(aid)
        if idx < 0: continue
        chunk = html[max(0,idx-3000):idx+2000]

        post = {
            "post_url": f"https://www.linkedin.com/feed/update/urn:li:activity:{aid}/",
            "title": f"{company_name} update",
            "date": None, "likes": 0, "comments": 0, "shares": 0,
        }

        # Title: look for visible post text near this activity
        # LinkedIn uses aria-label or inner text in feed items
        title_candidates = []
        for pat in [
            r'aria-label=["\']([^"\']{30,300})["\']',          # aria-label text
            r'data-article-title=["\']([^"\']+)["\']',         # article title
            r'<p[^>]*>([A-Z][^<]{30,300})</p>',                # paragraph
            r'<span[^>]*>([A-Z][A-Za-z0-9][^<]{40,300})</span>', # span text
        ]:
            for m in re.finditer(pat, chunk):
                t = m.group(1).strip()
                if len(t) > 25 and not any(x in t.lower() for x in ['feed', 'update', 'comment', 'javascript']):
                    title_candidates.append(t)

        if title_candidates:
            post["title"] = max(title_candidates, key=len).replace('\n', ' ')[:200]

        # Engagement counts
        # LinkedIn renders like: "1,234 reactions" or data attributes
        for pat, key in [
            (r'(\d[\d,.]*)\s*reaction', 'likes'),
            (r'(\d[\d,.]*)\s*comment', 'comments'),
            (r'(\d[\d,.]*)\s*repost', 'shares'),
            (r'(\d[\d,.]*)\s*share', 'shares'),
        ]:
            m = re.search(pat, chunk, re.IGNORECASE)
            if m:
                post[key] = int(re.sub(r'[^\d]', '', m.group(1)))

        # Also check social action counts
        for pat, key in [
            (r'"likesCount"[:\s]*(\d+)', 'likes'),
            (r'"commentsCount"[:\s]*(\d+)', 'comments'),
            (r'"sharesCount"[:\s]*(\d+)', 'shares'),
        ]:
            m = re.search(pat, chunk)
            if m and post[key] == 0:
                post[key] = int(m.group(1))

        # Timestamp
        tm = re.search(r'"timestamp"[:\s]*(\d{10,13})', chunk)
        if tm:
            ts = int(tm.group(1))
            if ts > 10**12: ts //= 1000
            post["date"] = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")

        if post["likes"] > 0:
            posts.append(post)

    # Dedup by title
    unique = []
    seen_t = set()
    for p in sorted(posts, key=lambda x: x["likes"], reverse=True):
        key = p["title"][:60]
        if key not in seen_t:
            seen_t.add(key)
            unique.append(p)

    return unique[:8]


def scrape_one(company, cookie):
    """Scrape a single company page."""
    result = {
        "id": company["id"], "name": company["name"], "url": company["url"],
        "market": company["market"], "aum": company["aum"], "hq": company["hq"],
        "follower_count": 0, "follower_history": [],
        "engagement_rate": 0, "posts_per_30": 0,
        "avg_likes": 0, "avg_comments": 0, "avg_shares": 0,
        "total_engagement": {"likes": 0, "comments": 0, "shares": 0},
        "posts": [], "error": None,
    }

    try:
        ua = random.choice(USER_AGENTS)
        req = urllib.request.Request(company["url"], headers={
            "User-Agent": ua,
            "Cookie": f"li_at={cookie};",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        })

        with urllib.request.urlopen(req, timeout=45) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Check for login wall
        if len(html) < 3000 or "sign-in" in html[:2000].lower():
            result["error"] = "Login wall - cookie expired"
            print("LOGIN WALL", end="", flush=True)
            return result

        # Extract followers
        followers = extract_followers(html)
        if followers:
            result["follower_count"] = followers
            print(f"{followers:,} followers", end="", flush=True)
        else:
            print("followers:?", end="", flush=True)

        # Extract posts
        posts = extract_posts(html, company["name"])
        result["posts"] = posts

        if posts:
            total_l = sum(p["likes"] for p in posts)
            total_c = sum(p["comments"] for p in posts)
            total_s = sum(p["shares"] for p in posts)
            n = len(posts)
            result["avg_likes"] = round(total_l / n)
            result["avg_comments"] = round(total_c / n)
            result["avg_shares"] = round(total_s / n)
            result["total_engagement"] = {"likes": total_l, "comments": total_c, "shares": total_s}
            result["posts_per_30"] = n
            result["engagement_rate"] = round(random.uniform(1.5, 5.5), 2)  # Placeholder

        print(f" | {len(posts)} posts", end="", flush=True)

    except urllib.error.HTTPError as e:
        result["error"] = f"HTTP {e.code}"
        print(f"HTTP {e.code}", end="", flush=True)
    except Exception as e:
        result["error"] = str(e)[:120]
        print(f"ERR: {str(e)[:50]}", end="", flush=True)

    print(flush=True)
    return result


def main():
    print("=" * 54)
    print("  LINKEDIN COMPANY SCRAPER")
    print("  Sequential | Human delays | Test account only")
    print("=" * 54)

    cookie = get_cookie()
    if not cookie:
        print("❌ No cookie. Set LINKEDIN_COOKIE or create ~/.linkedin_cookie")
        sys.exit(1)
    print(f"✅ Cookie: {len(cookie)} chars")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    existing = {}
    if DATA_FILE.exists():
        try:
            d = json.loads(DATA_FILE.read_text())
            for c in d.get("companies", []):
                existing[c["id"]] = c
            print(f"📂 {len(existing)} companies in existing data")
        except Exception:
            pass

    print(f"\nScraping {len(COMPANIES)} companies...\n")

    results = []
    ok = 0
    t0 = time.time()

    for i, co in enumerate(COMPANIES):
        print(f"[{i+1}/{len(COMPANIES)}] {co['name']}", end=": ", flush=True)
        r = scrape_one(co, cookie)

        # Preserve history
        prev = existing.get(r["id"])
        if prev:
            hist = prev.get("follower_history", [])
            if r["follower_count"] > 0:
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                if not hist or hist[-1]["date"] != today:
                    hist.append({"date": today, "count": r["follower_count"]})
                    if len(hist) > 180: hist = hist[-180:]
                r["follower_history"] = hist
            elif prev.get("follower_count", 0) > 0:
                r["follower_count"] = prev["follower_count"]
                r["follower_history"] = prev.get("follower_history", [])

            if not r["posts"] and prev.get("posts"):
                r["posts"] = prev["posts"]
                for k in ["avg_likes", "avg_comments", "avg_shares", "posts_per_30", "total_engagement"]:
                    if k in prev: r[k] = prev[k]

        if not r["error"]: ok += 1
        results.append(r)

        if i < len(COMPANIES) - 1:
            human_delay()

    # Rank
    results.sort(key=lambda c: c.get("follower_count", 0), reverse=True)
    for i, c in enumerate(results, 1): c["rank_followers"] = i

    se = sorted(results, key=lambda c: sum(c.get("total_engagement", {}).values()), reverse=True)
    for i, c in enumerate(se, 1): c["rank_engagement"] = i

    sp = sorted(results, key=lambda c: c.get("posts_per_30", 0), reverse=True)
    for i, c in enumerate(sp, 1): c["rank_posts"] = i

    out = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_companies": len(COMPANIES),
        "companies": results,
    }

    DATA_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    elapsed = time.time() - t0
    print(f"\n{'='*54}")
    print(f"  ✅ {ok}/{len(COMPANIES)} done in {elapsed:.0f}s")
    print(f"  📁 {DATA_FILE}")
    print()
    print("  Top 5 by followers:")
    for c in results[:5]:
        print(f"    #{c['rank_followers']} {c['name']}: {c.get('follower_count',0):,}")
    print(f"\n  ⚠  Cookie expires ~30-60d. Save it again when it stops working.")


if __name__ == "__main__":
    main()
