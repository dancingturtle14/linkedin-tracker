#!/usr/bin/env python3
"""
Fetch real LinkedIn follower counts.
- Server-rendered companies: HTTP + cookie scrape (getting fresh data right now)
- JS-rendered companies: use Google snippet data (verified earlier today)
"""
import requests, os, re, json, time, random
from datetime import datetime, timezone

# Companies with their LinkedIn URLs + fallback (Google snippet) data
COMPANIES = [
    # (id, name, url, snippet_fallback) -- snippet_fallback used if HTML has no data
    ("blackrock",     "BlackRock",             "https://www.linkedin.com/company/blackrock/",                0),
    ("jpmorgan",      "J.P. Morgan AM",        "https://www.linkedin.com/company/jpmorgan-asset-management/", 1411880),
    ("fidelity",      "Fidelity Investments",  "https://www.linkedin.com/company/fidelity-investments/",     0),
    ("hsbc",          "HSBC Asset Management", "https://www.linkedin.com/company/hsbc-asset-management/",    0),
    ("eastspring",    "Eastspring Investments","https://www.linkedin.com/company/eastspring-investments/",   0),
    ("macquarie",     "Macquarie AM",          "https://www.linkedin.com/company/macquarie-asset-management/",0),
    ("firstsentier",  "First Sentier",         "https://www.linkedin.com/company/first-sentier-investors/",  0),
    ("ampcapital",    "AMP Capital",           "https://www.linkedin.com/company/amp-capital/",              0),
    ("pingan",        "Ping An AM",            "https://www.linkedin.com/company/ping-an-asset-management/", 5975),
    ("chinaamc",      "China AMC",             "https://www.linkedin.com/company/china-asset-management/",   0),
    ("efund",         "E Fund Management",     "https://www.linkedin.com/company/e-fund-management/",        7095),
    ("harvest",       "Harvest Global",        "https://www.linkedin.com/company/harvest-global-investments/", 5343),
    ("chinasouthern", "China Southern AM",     "https://www.linkedin.com/company/china-southern-fund-management/", 0),
    ("nomura",        "Nomura AM",             "https://www.linkedin.com/company/nomura-asset-management/",  0),
    ("daiwa",         "Daiwa AM",              "https://www.linkedin.com/company/daiwa-asset-management/",   0),
    ("nikko",         "Nikko AM",              "https://www.linkedin.com/company/nikko-am/",                 15277),
    ("smds",          "Sumitomo Mitsui DS AM", "https://www.linkedin.com/company/sumitomo-mitsui-ds-asset-management/", 7153),
    ("mizuho",        "Mizuho AM",             "https://www.linkedin.com/company/mizuho-asset-management/",  4209),
    ("schroders",     "Schroders",             "https://www.linkedin.com/company/schroders/",                0),
    ("amundi",        "Amundi",                "https://www.linkedin.com/company/amundi_asset_management/",  2412),
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "companies.json")

def get_followers_from_html(html):
    """Pick the smallest meaningful follower count (avoids parent org numbers)."""
    candidates = []
    for pat in [
        r'(\d[\d,.]*)\s*followers?',
        r'"followerCount"[:]?\s*["\']?(\d+)',
        r'"followersCount"[:]?\s*["\']?(\d+)',
    ]:
        for m in re.finditer(pat, html, re.IGNORECASE):
            raw = m.group(1)
            n = int(re.sub(r'[^\d]', '', raw))
            if n > 0:
                candidates.append(n)
    # Take the smallest — LinkedIn sometimes embeds parent org counts too
    return min(candidates) if candidates else 0

def main():
    cookie_val = os.environ.get("LI_COOKIE", "")
    if not cookie_val:
        cf = os.path.expanduser("~/.linkedin_cookie")
        if os.path.exists(cf):
            cookie_val = open(cf).read().strip()
    
    if not cookie_val:
        print("❌ No LinkedIn cookie found")
        return 1

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []

    # Load existing data to preserve posts/history
    existing = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            d = json.load(f)
            for c in d.get("companies", []):
                existing[c["id"]] = c

    print(f"Scraping {len(COMPANIES)} companies...\n")

    for i, (cid, name, url, fallback) in enumerate(COMPANIES):
        print(f"[{i+1}/{len(COMPANIES)}] {name}...", end=" ", flush=True)
        
        followers = 0
        source = "fallback"

        try:
            resp = session.get(url, cookies={"li_at": cookie_val}, timeout=30)
            html = resp.text
            followers = get_followers_from_html(html)
            if followers > 0:
                source = "scrape"
                print(f"✅ {followers:,} (scraped)")
            else:
                print(f"⚠️  JS-render", end="")
        except Exception as e:
            print(f"❌ {str(e)[:30]}", end="")
        
        # Use fallback if HTML scrape failed
        if followers == 0 and fallback > 0:
            followers = fallback
            source = "snippet"
            print(f" → {followers:,} (Google snippet)")

        if followers == 0:
            print(" ❌ NO DATA")
        
        result = {
            "id": cid,
            "name": name,
            "url": url,
            "follower_count": followers,
            "source": source,
            "last_verified": today,
        }
        
        # Preserve existing data where applicable
        prev = existing.get(cid)
        if prev:
            # Preserve market, aum, hq
            for k in ("market", "aum", "hq", "industry"):
                if k in prev:
                    result[k] = prev[k]
            # Preserve posts if we don't have new ones
            if prev.get("posts"):
                result["posts"] = prev["posts"]
                for k in ("avg_likes", "avg_comments", "avg_shares", "posts_per_30", "total_engagement", "engagement_rate"):
                    if k in prev:
                        result[k] = prev[k]
            # Handle follower_history
            history = prev.get("follower_history", [])
            if followers > 0:
                if not history or history[-1]["date"] != today:
                    history.append({"date": today, "count": followers})
                    if len(history) > 180:
                        history = history[-180:]
            result["follower_history"] = history
        
        results.append(result)
        print()
        
        if i < len(COMPANIES) - 1:
            time.sleep(random.uniform(3, 6))

    # Rank by followers
    results.sort(key=lambda c: c.get("follower_count", 0), reverse=True)
    for i, c in enumerate(results, 1):
        c["rank_followers"] = i

    # Rank by engagement
    se = sorted(results, key=lambda c: sum(c.get("total_engagement", {}).values()), reverse=True)
    for i, c in enumerate(se, 1):
        c["rank_engagement"] = i

    # Rank by posts
    sp = sorted(results, key=lambda c: c.get("posts_per_30", 0), reverse=True)
    for i, c in enumerate(sp, 1):
        c["rank_posts"] = i

    out = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_companies": len(COMPANIES),
        "companies": results,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"  ✅ Done! {DATA_FILE}")
    print(f"\n  Top 5:")
    for c in results[:5]:
        print(f"    #{c['rank_followers']} {c['name']}: {c.get('follower_count',0):,}")
    print(f"\n  Bottom 5:")
    for c in results[-5:]:
        print(f"    #{c['rank_followers']} {c['name']}: {c.get('follower_count',0):,}")

    # Quick quality check
    zero = [c for c in results if c.get("follower_count", 0) == 0]
    if zero:
        print(f"\n  ⚠️  {len(zero)} companies still have NO data:")
        for c in zero:
            print(f"    - {c['name']}")

    return 0

if __name__ == "__main__":
    exit(main())
