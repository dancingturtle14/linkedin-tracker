#!/usr/bin/env python3
"""
Daily LinkedIn tracker data updater.
- HTTP + cookie scrape for companies that can be scraped
- Preserves last known values for companies that require JS rendering
- Pushes updated data to GitHub Pages

Usage: LI_COOKIE="xxx" python3 scraper/daily_update.py
"""
import requests, os, re, json, time, random, sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
REPO_DIR = SCRIPT_DIR.parent
DATA_FILE = REPO_DIR / "data" / "companies.json"

# Companies that CAN be scraped via HTTP + cookie
HTTP_SCRAPEABLE = [
    ("blackrock",     "BlackRock",             "https://www.linkedin.com/company/blackrock/"),
    ("jpmorgan",      "J.P. Morgan",           "https://www.linkedin.com/company/jpmorgan/"),
    ("fidelity",      "Fidelity Investments",  "https://www.linkedin.com/company/fidelity-investments/"),
    ("schroders",     "Schroders",             "https://www.linkedin.com/company/schroders/"),
    ("mizuho",        "Mizuho",                "https://www.linkedin.com/company/mizuho/"),
    ("macquarie",     "Macquarie AM",          "https://www.linkedin.com/company/macquarie-asset-management/"),
    ("eastspring",    "Eastspring Investments","https://www.linkedin.com/company/eastspring-investments/"),
    ("ampcapital",    "AMP Capital",           "https://www.linkedin.com/company/amp-capital/"),
    ("nomura",        "Nomura AM",             "https://www.linkedin.com/company/nomura-asset-management/"),
    ("hsbc",          "HSBC Asset Management", "https://www.linkedin.com/company/hsbc-asset-management/"),
    ("firstsentier",  "First Sentier",         "https://www.linkedin.com/company/first-sentier-investors/"),
    ("chinaamc",      "China AMC",             "https://www.linkedin.com/company/china-asset-management/"),
    ("chinasouthern", "China Southern AM",     "https://www.linkedin.com/company/china-southern-fund-management/"),
    ("daiwa",         "Daiwa AM",              "https://www.linkedin.com/company/daiwa-asset-management/"),
]

# Companies that REQUIRE JS rendering — keep last known value
JS_RENDER_COMPANIES = {
    "amundi":  "https://www.linkedin.com/company/amundi/",
    "nikko":   "https://www.linkedin.com/company/nikko-asset-management/",
    "smds":    "https://www.linkedin.com/company/sumitomo-mitsui-ds-asset-management/",
    "pingan":  "https://www.linkedin.com/company/ping-an-asset-management/",
    "efund":   "https://www.linkedin.com/company/e-fund-management/",
    "harvest": "https://www.linkedin.com/company/harvest-global-investments/",
}


def get_followers_from_html(html):
    """Extract follower count from HTML meta description (most reliable)."""
    m = re.search(r'(\d[\d,]*)\s*followers?\s*on\s*LinkedIn', html, re.IGNORECASE)
    if m:
        return int(m.group(1).replace(',', ''))
    return 0


def main():
    cookie_val = os.environ.get("LI_COOKIE", "")
    if not cookie_val:
        path = Path.home() / ".linkedin_cookie"
        if path.exists():
            cookie_val = path.read_text().strip()

    if not cookie_val:
        print("❌ No LinkedIn cookie. Set LI_COOKIE env or create ~/.linkedin_cookie")
        return 1

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Load existing data
    existing = {}
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            for c in json.load(f).get("companies", []):
                existing[c["id"]] = c

    results = []
    scraped_ok = 0
    preserved = 0
    all_companies = list(HTTP_SCRAPEABLE) + [
        (cid, cid, url) for cid, url in JS_RENDER_COMPANIES.items()
    ]

    print(f"LinkedIn Tracker — Daily Update ({today})")
    print(f"{'='*50}")
    print(f"Total: {len(all_companies)} companies ({len(HTTP_SCRAPEABLE)} scrapeable, {len(JS_RENDER_COMPANIES)} JS-only)\n")

    for i, (cid, name, url) in enumerate(all_companies):
        print(f"[{i+1}/{len(all_companies)}] {name:<30s}", end=" ", flush=True)

        followers = 0
        source = "none"
        error = None
        prev = existing.get(cid, {})

        # Try HTTP scrape first
        if cid in [c[0] for c in HTTP_SCRAPEABLE]:
            try:
                resp = session.get(url, timeout=45)
                followers = get_followers_from_html(resp.text)
                if followers > 0:
                    scraped_ok += 1
                    source = "scrape"
                    print(f"✅ {followers:>8,}")
                else:
                    print(f"⚠️  no followers found")
            except Exception as e:
                error = str(e)[:60]
                print(f"❌ {error}")

        # For JS-rendered companies: preserve last known value
        if cid in JS_RENDER_COMPANIES:
            if prev and prev.get("follower_count", 0) > 0:
                followers = prev["follower_count"]
                preserved += 1
                source = "preserved"
                print(f"🔄 {followers:>8,} (preserved)")
            else:
                print(f"⚠️  no previous data")

        # Build result object
        result = {
            "id": cid,
            "name": prev.get("name", name.capitalize()),
            "url": url,
            "market": prev.get("market", ""),
            "aum": prev.get("aum", ""),
            "hq": prev.get("hq", ""),
            "industry": prev.get("industry", "Asset Management"),
            "follower_count": followers,
            "follower_history": prev.get("follower_history", []),
            "engagement_rate": prev.get("engagement_rate", 0),
            "posts_per_30": prev.get("posts_per_30", 0),
            "avg_likes": prev.get("avg_likes", 0),
            "avg_comments": prev.get("avg_comments", 0),
            "avg_shares": prev.get("avg_shares", 0),
            "total_engagement": prev.get("total_engagement", {"likes": 0, "comments": 0, "shares": 0}),
            "posts": prev.get("posts", []),
            "rank_followers": 0,
            "rank_engagement": 0,
            "rank_posts": 0,
            "error": error,
        }

        # Update follower_history for new scrapes
        if followers > 0 and source == "scrape":
            hist = result["follower_history"]
            if not hist or hist[-1]["date"] != today:
                hist.append({"date": today, "count": followers})
                if len(hist) > 180:
                    result["follower_history"] = hist[-180:]

        results.append(result)

        if i < len(all_companies) - 1 and source == "scrape":
            time.sleep(random.uniform(8, 14))

    # Re-rank
    results.sort(key=lambda c: c.get("follower_count", 0), reverse=True)
    for i, c in enumerate(results, 1):
        c["rank_followers"] = i

    se = sorted(results, key=lambda c: sum(c.get("total_engagement", {}).values()), reverse=True)
    for i, c in enumerate(se, 1):
        c["rank_engagement"] = i

    sp = sorted(results, key=lambda c: c.get("posts_per_30", 0), reverse=True)
    for i, c in enumerate(sp, 1):
        c["rank_posts"] = i

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_companies": len(all_companies),
        "companies": results,
    }

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"  ✓ {scraped_ok} scraped + {preserved} preserved = {scraped_ok+preserved}/{len(all_companies)}")
    print(f"  📁 {DATA_FILE}")
    print(f"\n  Top 5:")
    for c in results[:5]:
        print(f"    #{c['rank_followers']} {c['name']:<30s} {c['follower_count']:>8,}")

    # Push to GitHub Pages
    print(f"\n  📤 Pushing to GitHub Pages...")
    result = os.system(f"cd {REPO_DIR} && git add data/companies.json && git commit --allow-empty -m 'chore: daily data update {today}' && git push origin main 2>&1")

    if result == 0:
        print(f"  ✅ GitHub Pages updated!")
    else:
        print(f"  ⚠️ Git push exit code: {result}")

    return 0


if __name__ == "__main__":
    exit(main())
