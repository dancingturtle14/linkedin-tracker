#!/usr/bin/env python3
"""
linkedin_scraper.py — Scrape LinkedIn company data using Scrapling + cookies.
Requires a LinkedIn session cookie (li_at) for authenticated access.

Usage:
  # Set session cookie first
  export LINKEDIN_COOKIE="AQED...your_li_at_cookie..."
  python3 linkedin_scraper.py

  # Or provide via file
  echo "AQED...cookie..." > ~/.linkedin_cookie
  python3 linkedin_scraper.py

Output: ../data/companies.json
"""

import json, os, sys, time, re
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_FILE = DATA_DIR / "companies.json"

# ── Companies to scrape ──
COMPANIES = [
    {"id": "blackrock",         "name": "BlackRock",                "url": "https://www.linkedin.com/company/blackrock/",                "market": "Global",    "aum": "$11.5T", "hq": "USA"},
    {"id": "jpmorgan",          "name": "J.P. Morgan AM",           "url": "https://www.linkedin.com/company/jpmorgan-asset-management/", "market": "Global",    "aum": "$4.0T",  "hq": "USA"},
    {"id": "fidelity",          "name": "Fidelity Investments",     "url": "https://www.linkedin.com/company/fidelity-investments/",     "market": "Global",    "aum": "$5.5T",  "hq": "USA"},
    {"id": "hsbc",              "name": "HSBC Asset Management",    "url": "https://www.linkedin.com/company/hsbc-asset-management/",    "market": "Hong Kong", "aum": "$600B+", "hq": "HK"},
    {"id": "eastspring",        "name": "Eastspring Investments",   "url": "https://www.linkedin.com/company/eastspring-investments/",   "market": "Singapore", "aum": "$200B+", "hq": "Singapore"},
    {"id": "macquarie",         "name": "Macquarie AM",             "url": "https://www.linkedin.com/company/macquarie-asset-management/", "market": "Australia", "aum": "$450B+", "hq": "Australia"},
    {"id": "firstsentier",      "name": "First Sentier",            "url": "https://www.linkedin.com/company/first-sentier-investors/",  "market": "Australia", "aum": "$150B+", "hq": "Australia"},
    {"id": "ampcapital",        "name": "AMP Capital",              "url": "https://www.linkedin.com/company/amp-capital/",              "market": "Australia", "aum": "$150B+", "hq": "Australia"},
    {"id": "pingan",            "name": "Ping An AM",               "url": "https://www.linkedin.com/company/ping-an-asset-management/", "market": "China",     "aum": "$500B+", "hq": "China"},
    {"id": "chinaamc",          "name": "China AMC",                "url": "https://www.linkedin.com/company/china-asset-management/",   "market": "China",     "aum": "$250B+", "hq": "China"},
    {"id": "efund",             "name": "E Fund Management",        "url": "https://www.linkedin.com/company/e-fund-management/",        "market": "China",     "aum": "$200B+", "hq": "China"},
    {"id": "harvest",           "name": "Harvest Global",           "url": "https://www.linkedin.com/company/harvest-global-investments/", "market": "China",     "aum": "$150B+", "hq": "China"},
    {"id": "chinasouthern",     "name": "China Southern AM",        "url": "https://www.linkedin.com/company/china-southern-fund-management/", "market": "China", "aum": "$200B+", "hq": "China"},
    {"id": "nomura",            "name": "Nomura AM",                "url": "https://www.linkedin.com/company/nomura-asset-management/",  "market": "Japan",     "aum": "$500B+", "hq": "Japan"},
    {"id": "daiwa",             "name": "Daiwa AM",                 "url": "https://www.linkedin.com/company/daiwa-asset-management/",   "market": "Japan",     "aum": "$200B+", "hq": "Japan"},
    {"id": "nikko",             "name": "Nikko AM",                 "url": "https://www.linkedin.com/company/nikko-am/",                 "market": "Japan",     "aum": "$200B+", "hq": "Japan"},
    {"id": "smds",              "name": "Sumitomo Mitsui DS AM",    "url": "https://www.linkedin.com/company/sumitomo-mitsui-ds-asset-management/", "market": "Japan", "aum": "$150B+", "hq": "Japan"},
    {"id": "mizuho",            "name": "Mizuho AM",                "url": "https://www.linkedin.com/company/mizuho-asset-management/",  "market": "Japan",     "aum": "$100B+", "hq": "Japan"},
    {"id": "schroders",         "name": "Schroders",                "url": "https://www.linkedin.com/company/schroders/",                "market": "Global",    "aum": "$800B+", "hq": "UK"},
    {"id": "amundi",            "name": "Amundi",                   "url": "https://www.linkedin.com/company/amundi_asset_management/",  "market": "Global",    "aum": "$2.3T",  "hq": "France"},
]

# ── Cookie: try env var, then file ──
def get_cookie():
    cookie = os.environ.get("LINKEDIN_COOKIE", "")
    if not cookie:
        try:
            cookie_file = Path.home() / ".linkedin_cookie"
            if cookie_file.exists():
                cookie = cookie_file.read_text().strip()
        except:
            pass
    return cookie

# ── Scraping ──
def scrape_company(company, cookie):
    """Scrape a single LinkedIn company page for follower count and recent posts."""
    from scrapling.fetchers import StealthyFetcher
    # Enable adaptive mode
    StealthyFetcher.adaptive = True

    result = {
        "id": company["id"],
        "name": company["name"],
        "url": company["url"],
        "market": company["market"],
        "aum": company["aum"],
        "hq": company["hq"],
        "follower_count": 0,
        "follower_history": [],
        "posts": [],
        "error": None
    }

    try:
        print(f"  Fetching {company['name']}...", end=" ", flush=True)

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        if cookie:
            headers["Cookie"] = f"li_at={cookie};"
            print("(authed)", end=" ", flush=True)

        page = StealthyFetcher.fetch(
            company["url"],
            headless=True,
            network_idle=True,
            headers=headers,
            timeout=30
        )

        text = page.text or ""

        # --- Extract follower count ---
        # Various patterns LinkedIn uses
        follower_patterns = [
            r'(\d[\d,.]*)\s*followers',
            r'followers["\']>[^<]*?(\d[\d,.]*)',
            r'(\d[\d,.]*)\s*followers?\s*',
            r'"followerCount":(\d+)',
            r'(\d[\d,.]*)\s*follower',
        ]
        for pat in follower_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                raw = m.group(1)
                followers = int(re.sub(r'[^\d]', '', raw))
                if followers > 0:
                    result["follower_count"] = followers
                    print(f"{followers:,} followers", end="", flush=True)
                    break

        if result["follower_count"] == 0:
            print("followers: not found", end="", flush=True)

        # --- Extract recent posts ---
        # Look for feed update activity items
        post_section_start = text.find('feed-shared-update-v2')
        if post_section_start == -1:
            post_section_start = text.find('occludable-update')
        if post_section_start == -1:
            post_section_start = text.find('update-components-article')

        if post_section_start >= 0:
            # Try to find post data in the page
            # LinkedIn often embeds post data in JSON-like structures or data-attributes
            # Pattern 1: look for urn:li:activity: identifiers
            activity_ids = re.findall(r'urn:li:activity:(\d+)', text)
            seen_ids = set()

            for i, act_id in enumerate(activity_ids[:10]):
                if act_id in seen_ids:
                    continue
                seen_ids.add(act_id)

                # Look for this post's details
                post_data = {
                    "post_url": f"https://www.linkedin.com/feed/update/urn:li:activity:{act_id}/",
                    "title": f"LinkedIn post",
                    "date": None,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "activity_id": act_id
                }

                # Try to find post text near this activity ID
                idx = text.find(act_id)
                if idx >= 0:
                    chunk = text[max(0, idx-2000):idx+2000]
                    # Find post text/title
                    text_matches = re.findall(r'[<>]?([A-Z][A-Za-z0-9][^<>]{20,200}[.?])', chunk)
                    if text_matches:
                        # Pick the longest meaningful text
                        meaningful = [t for t in text_matches if len(t) > 20 and 'feed' not in t.lower() and 'update' not in t.lower()]
                        if meaningful:
                            post_data["title"] = max(meaningful, key=len).strip()

                    # Find engagement counts
                    like_m = re.search(r'(\d+)\s*reaction', chunk, re.IGNORECASE)
                    if like_m: post_data["likes"] = int(like_m.group(1))

                    comment_m = re.search(r'(\d+)\s*comment', chunk, re.IGNORECASE)
                    if comment_m: post_data["comments"] = int(comment_m.group(1))

                if post_data["likes"] > 0 or post_data["comments"] > 0:
                    result["posts"].append(post_data)

        # Sort posts by likes desc
        result["posts"].sort(key=lambda p: p["likes"], reverse=True)

        print(f" | {len(result['posts'])} posts")
        time.sleep(2)  # Rate limiting

    except Exception as e:
        result["error"] = str(e)[:100]
        print(f"ERROR: {str(e)[:60]}")

    return result


# ── Main ──
def main():
    cookie = get_cookie()
    if not cookie:
        print("⚠ No LinkedIn cookie found!")
        print(f"  Set LINKEDIN_COOKIE env var or create ~/.linkedin_cookie")
        print(f"  Cookie = your LinkedIn 'li_at' session token")
        print("\nWithout cookie, limited public data may be available.\n")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Try to load existing data for history
    existing_data = {}
    if DATA_FILE.exists():
        try:
            existing = json.loads(DATA_FILE.read_text())
            for c in existing.get("companies", []):
                existing_data[c["id"]] = c
        except:
            pass

    print(f"Scraping {len(COMPANIES)} companies...\n")
    companies_data = []

    for i, company in enumerate(COMPANIES):
        print(f"[{i+1}/{len(COMPANIES)}] ", end="")
        result = scrape_company(company, cookie)

        # Preserve follower history from existing data
        prev = existing_data.get(result["id"])
        if prev and prev.get("follower_count", 0) > 0:
            history = prev.get("follower_history", [])
            if result["follower_count"] > 0 and (not history or history[-1]["count"] != result["follower_count"]):
                history.append({
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "count": result["follower_count"]
                })
                if len(history) > 90:
                    history = history[-90:]
            result["follower_history"] = history

        companies_data.append(result)

    # Build output
    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_companies": len(COMPANIES),
        "companies": companies_data
    }

    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n✅ Saved {len(COMPANIES)} companies to {DATA_FILE}")


if __name__ == "__main__":
    main()
