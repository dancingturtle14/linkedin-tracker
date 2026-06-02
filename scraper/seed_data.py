#!/usr/bin/env python3
"""
seed_data.py — Generate realistic seed data for the LinkedIn Tracker dashboard.
This populates companies.json with approximate real-world follower counts
and simulated post data so the dashboard always has data to display.

Run: python3 seed_data.py
Output: ../data/companies.json
"""

import json, random, math
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_FILE = DATA_DIR / "companies.json"

random.seed(42)

COMPANIES_DATA = [
    {"id": "blackrock",     "name": "BlackRock",             "url": "https://www.linkedin.com/company/blackrock/",                "market": "Global",    "aum": "$11.5T", "hq": "USA",     "base_followers": 1950000, "industry": "Investment Management"},
    {"id": "jpmorgan",      "name": "J.P. Morgan AM",        "url": "https://www.linkedin.com/company/jpmorgan-asset-management/", "market": "Global",    "aum": "$4.0T",  "hq": "USA",     "base_followers": 825000,  "industry": "Investment Management"},
    {"id": "fidelity",      "name": "Fidelity Investments",  "url": "https://www.linkedin.com/company/fidelity-investments/",     "market": "Global",    "aum": "$5.5T",  "hq": "USA",     "base_followers": 1480000, "industry": "Financial Services"},
    {"id": "hsbc",          "name": "HSBC Asset Management", "url": "https://www.linkedin.com/company/hsbc-asset-management/",    "market": "Hong Kong", "aum": "$600B+", "hq": "HK",      "base_followers": 410000,  "industry": "Asset Management"},
    {"id": "eastspring",    "name": "Eastspring Investments","url": "https://www.linkedin.com/company/eastspring-investments/",   "market": "Singapore", "aum": "$200B+", "hq": "Singapore","base_followers": 155000,  "industry": "Asset Management"},
    {"id": "macquarie",     "name": "Macquarie AM",          "url": "https://www.linkedin.com/company/macquarie-asset-management/", "market": "Australia", "aum": "$450B+", "hq": "Australia","base_followers": 295000,  "industry": "Asset Management"},
    {"id": "firstsentier",  "name": "First Sentier",         "url": "https://www.linkedin.com/company/first-sentier-investors/",  "market": "Australia", "aum": "$150B+", "hq": "Australia","base_followers": 98000,   "industry": "Investment Management"},
    {"id": "ampcapital",    "name": "AMP Capital",           "url": "https://www.linkedin.com/company/amp-capital/",              "market": "Australia", "aum": "$150B+", "hq": "Australia","base_followers": 185000,  "industry": "Asset Management"},
    {"id": "pingan",        "name": "Ping An AM",            "url": "https://www.linkedin.com/company/ping-an-asset-management/", "market": "China",     "aum": "$500B+", "hq": "China",    "base_followers": 78000,   "industry": "Asset Management"},
    {"id": "chinaamc",      "name": "China AMC",             "url": "https://www.linkedin.com/company/china-asset-management/",   "market": "China",     "aum": "$250B+", "hq": "China",    "base_followers": 52000,   "industry": "Asset Management"},
    {"id": "efund",         "name": "E Fund Management",     "url": "https://www.linkedin.com/company/e-fund-management/",        "market": "China",     "aum": "$200B+", "hq": "China",    "base_followers": 45000,   "industry": "Asset Management"},
    {"id": "harvest",       "name": "Harvest Global",        "url": "https://www.linkedin.com/company/harvest-global-investments/", "market": "China",    "aum": "$150B+", "hq": "China",    "base_followers": 38000,   "industry": "Investment Management"},
    {"id": "chinasouthern", "name": "China Southern AM",     "url": "https://www.linkedin.com/company/china-southern-fund-management/", "market": "China", "aum": "$200B+", "hq": "China",  "base_followers": 35000,   "industry": "Asset Management"},
    {"id": "nomura",        "name": "Nomura AM",             "url": "https://www.linkedin.com/company/nomura-asset-management/",  "market": "Japan",     "aum": "$500B+", "hq": "Japan",    "base_followers": 210000,  "industry": "Asset Management"},
    {"id": "daiwa",         "name": "Daiwa AM",              "url": "https://www.linkedin.com/company/daiwa-asset-management/",   "market": "Japan",     "aum": "$200B+", "hq": "Japan",    "base_followers": 95000,   "industry": "Asset Management"},
    {"id": "nikko",         "name": "Nikko AM",              "url": "https://www.linkedin.com/company/nikko-am/",                 "market": "Japan",     "aum": "$200B+", "hq": "Japan",    "base_followers": 72000,   "industry": "Asset Management"},
    {"id": "smds",          "name": "Sumitomo Mitsui DS AM", "url": "https://www.linkedin.com/company/sumitomo-mitsui-ds-asset-management/", "market": "Japan", "aum": "$150B+", "hq": "Japan", "base_followers": 48000,   "industry": "Asset Management"},
    {"id": "mizuho",        "name": "Mizuho AM",             "url": "https://www.linkedin.com/company/mizuho-asset-management/",  "market": "Japan",     "aum": "$100B+", "hq": "Japan",    "base_followers": 55000,   "industry": "Asset Management"},
    {"id": "schroders",     "name": "Schroders",             "url": "https://www.linkedin.com/company/schroders/",                "market": "Global",    "aum": "$800B+", "hq": "UK",      "base_followers": 530000,  "industry": "Asset Management"},
    {"id": "amundi",        "name": "Amundi",                "url": "https://www.linkedin.com/company/amundi_asset_management/",  "market": "Global",    "aum": "$2.3T",  "hq": "France",  "base_followers": 265000,  "industry": "Asset Management"},
]

POST_TEMPLATES = [
    "2025 APAC Market Outlook: {theme}",
    "ESG Integration in Fixed Income: {theme}",
    "China A-Share Market: {theme}",
    "Japan Equity Reform Story: {theme}",
    "Private Credit in Asia Pacific: {theme}",
    "Navigating the Rate Cycle: {theme}",
    "India Growth Trajectory: {theme}",
    "Sustainable Investing: {theme}",
    "AI in Asset Management: {theme}",
    "Hong Kong IPO Market: {theme}",
    "Australian Super Trends: {theme}",
    "Singapore Family Office: {theme}",
    "Green Bonds Growth: {theme}",
    "Retirement in Ageing Asia: {theme}",
    "Global Macro Outlook: {theme}",
    "Real Estate Debt: {theme}",
    "Active vs Passive: {theme}",
    "Climate Risk: {theme}",
    "Cross-Border Capital Flows: {theme}",
    "Digital Asset Adoption: {theme}",
]

THEMES = [
    "Key Themes for the Year Ahead",
    "A Practical Framework",
    "Opportunities in the Recovery Cycle",
    "Corporate Governance Changes",
    "The Next Frontier",
    "Strategies for 2025",
    "Infrastructure and Demographics",
    "Emerging Market Perspectives",
    "Machine Learning Applications",
    "Signs of Recovery",
    "Trends and Opportunities",
    "A Regional Perspective",
    "Market Growth and Impact",
    "Challenges and Solutions",
    "Divergence and Dispersion",
    "Higher Rate Environment",
    "The APAC Perspective",
    "Portfolio Construction",
    "New Opportunities",
    "Institutional Update",
]

def generate_follower_history(base, days=90):
    """Generate a realistic follower growth time series."""
    history = []
    now = datetime.now(timezone.utc)
    growth_rate = random.uniform(0.0003, 0.002)  # Daily growth rate
    noise = random.uniform(0.003, 0.008)  # Daily noise
    for i in range(days, 0, -1):
        d = now - timedelta(days=i)
        growth = base * (1 + growth_rate) ** i
        jitter = growth * (1 + (random.random() - 0.5) * noise)
        history.append({
            "date": d.strftime("%Y-%m-%d"),
            "count": round(growth)
        })
    # Add today
    history.append({
        "date": now.strftime("%Y-%m-%d"),
        "count": round(base)
    })
    return history

def generate_posts(company_id, count=6):
    """Generate recent posts for a company."""
    posts = []
    now = datetime.now(timezone.utc)
    used_titles = set()
    for i in range(count):
        days_ago = random.randint(0, 28)
        post_date = now - timedelta(days=days_ago)
        template = random.choice(POST_TEMPLATES)
        theme = random.choice(THEMES)
        title = template.format(theme=theme)
        # Ensure unique
        suffix = 1
        orig = title
        while title in used_titles:
            title = f"{orig} ({suffix})"
            suffix += 1
        used_titles.add(title)

        base_eng = random.randint(50, 500)
        likes = round(base_eng * random.uniform(0.6, 0.85))
        comments = round(base_eng * random.uniform(0.05, 0.15))
        shares = round(base_eng * random.uniform(0.03, 0.1))

        posts.append({
            "post_url": f"https://www.linkedin.com/feed/update/urn:li:activity:{abs(hash(title)) % 10**12}/",
            "title": title,
            "date": post_date.strftime("%Y-%m-%d"),
            "likes": likes,
            "comments": comments,
            "shares": shares
        })

    posts.sort(key=lambda p: p["likes"], reverse=True)
    return posts

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    companies_output = []

    for c in COMPANIES_DATA:
        # Add some variation to follower count
        follower_count = c["base_followers"] + random.randint(-5000, 5000)
        follower_history = generate_follower_history(follower_count)

        # Engagement rate
        eng_rate = round(random.uniform(1.5, 5.5), 2)

        # Posts per 30 days
        posts_per_30 = random.randint(8, 40)

        # Avg engagement per post
        avg_likes = random.randint(80, 1200)
        avg_comments = random.randint(5, 80)
        avg_shares = random.randint(2, 40)

        # Total engagement
        total_likes = avg_likes * posts_per_30
        total_comments = avg_comments * posts_per_30
        total_shares = avg_shares * posts_per_30

        # Generate posts
        posts = generate_posts(c["id"], random.randint(4, 8))

        companies_output.append({
            "id": c["id"],
            "name": c["name"],
            "url": c["url"],
            "market": c["market"],
            "aum": c["aum"],
            "hq": c["hq"],
            "industry": c["industry"],
            "follower_count": follower_count,
            "follower_history": follower_history,
            "engagement_rate": eng_rate,
            "posts_per_30": posts_per_30,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_shares": avg_shares,
            "total_engagement": {
                "likes": total_likes,
                "comments": total_comments,
                "shares": total_shares
            },
            "posts": posts
        })

    # Sort by follower count desc (ranking)
    companies_output.sort(key=lambda c: c["follower_count"], reverse=True)

    # Add rank to each
    for i, c in enumerate(companies_output):
        c["rank_followers"] = i + 1

    # Rank by total engagement
    sorted_by_eng = sorted(companies_output, key=lambda c: c["total_engagement"]["likes"] + c["total_engagement"]["comments"] + c["total_engagement"]["shares"], reverse=True)
    eng_rank = {}
    for i, c in enumerate(sorted_by_eng):
        eng_rank[c["id"]] = i + 1

    # Rank by posts per 30
    sorted_by_posts = sorted(companies_output, key=lambda c: c["posts_per_30"], reverse=True)
    posts_rank = {}
    for i, c in enumerate(sorted_by_posts):
        posts_rank[c["id"]] = i + 1

    for c in companies_output:
        c["rank_engagement"] = eng_rank[c["id"]]
        c["rank_posts"] = posts_rank[c["id"]]

    output = {
        "last_updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_companies": len(COMPANIES_DATA),
        "companies": companies_output
    }

    DATA_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✅ Generated seed data for {len(companies_output)} companies")
    print(f"   Saved to {DATA_FILE}")
    print()
    print("Top 5 by followers:")
    for c in companies_output[:5]:
        print(f"   #{c['rank_followers']} {c['name']}: {c['follower_count']:,} followers")

if __name__ == "__main__":
    main()
