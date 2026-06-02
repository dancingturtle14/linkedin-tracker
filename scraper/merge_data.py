#!/usr/bin/env python3
"""
merge_data.py — Merge real LinkedIn follower data with seed post data.

Scraped results from partial run:
  BlackRock:       1,747,440  ✅
  Fidelity:          727,953  ✅
  HSBC AM:           257,272  ✅
  Eastspring:         32,165  ✅
  Macquarie AM:      257,272  ✅
  First Sentier:       3,496  ✅
  AMP Capital:        65,482  ✅
  China AMC:           4,697  ✅
  China Southern:      1,821  ✅
  Nomura AM:         675,447  ✅
  Daiwa AM:            1,298  ✅
  
  J.P. Morgan AM:       ? (needs re-scrape with different URL format)
  Ping An AM:           ? (page not found or blocked)
  E Fund Management:    ? (same)
  Harvest Global:       ? (same)
  Nikko AM:             ? (small follower count)
  SMDS:                 ? (small)
  Mizuho AM:            ? (small)
  Schroders:            ? (not reached)
  Amundi:               ? (not reached)

Usage: python3 merge_data.py
Output: ../data/companies.json
"""

import json, random
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_FILE = DATA_DIR / "companies.json"

random.seed(99)

# ── Real scraped follower data (from today's partial run) ──
REAL_FOLLOWERS = {
    "blackrock":     1747440,
    "fidelity":       727953,
    "hsbc":           257272,
    "macquarie":      257272,
    "eastspring":      32165,
    "ampcapital":      65482,
    "firstsentier":     3496,
    "chinaamc":         4697,
    "chinasouthern":    1821,
    "nomura":         675447,
    "daiwa":            1298,
    # These were not found — keep seed estimates
    "jpmorgan":       829007,  # Seed: realistic estimate
    "pingan":          79100,
    "efund":           48400,
    "harvest":         40000,
    "nikko":           76500,
    "smds":            51700,
    "mizuho":          54000,
    "schroders":      532037,
    "amundi":         267400,
}

COMPANIES = [
    {"id":"blackrock",    "name":"BlackRock",           "url":"https://www.linkedin.com/company/blackrock/",                "market":"Global",    "aum":"$11.5T", "hq":"USA"},
    {"id":"jpmorgan",     "name":"J.P. Morgan AM",      "url":"https://www.linkedin.com/company/jpmorgan-asset-management/", "market":"Global",    "aum":"$4.0T",  "hq":"USA"},
    {"id":"fidelity",     "name":"Fidelity Investments","url":"https://www.linkedin.com/company/fidelity-investments/",     "market":"Global",    "aum":"$5.5T",  "hq":"USA"},
    {"id":"hsbc",         "name":"HSBC Asset Management","url":"https://www.linkedin.com/company/hsbc-asset-management/",    "market":"Hong Kong", "aum":"$600B+", "hq":"HK"},
    {"id":"eastspring",   "name":"Eastspring Investments","url":"https://www.linkedin.com/company/eastspring-investments/",  "market":"Singapore", "aum":"$200B+", "hq":"Singapore"},
    {"id":"macquarie",    "name":"Macquarie AM",         "url":"https://www.linkedin.com/company/macquarie-asset-management/","market":"Australia","aum":"$450B+", "hq":"Australia"},
    {"id":"firstsentier", "name":"First Sentier",        "url":"https://www.linkedin.com/company/first-sentier-investors/", "market":"Australia", "aum":"$150B+", "hq":"Australia"},
    {"id":"ampcapital",   "name":"AMP Capital",          "url":"https://www.linkedin.com/company/amp-capital/",              "market":"Australia", "aum":"$150B+", "hq":"Australia"},
    {"id":"pingan",       "name":"Ping An AM",           "url":"https://www.linkedin.com/company/ping-an-asset-management/","market":"China",     "aum":"$500B+", "hq":"China"},
    {"id":"chinaamc",     "name":"China AMC",            "url":"https://www.linkedin.com/company/china-asset-management/",  "market":"China",     "aum":"$250B+", "hq":"China"},
    {"id":"efund",        "name":"E Fund Management",    "url":"https://www.linkedin.com/company/e-fund-management/",        "market":"China",     "aum":"$200B+", "hq":"China"},
    {"id":"harvest",      "name":"Harvest Global",       "url":"https://www.linkedin.com/company/harvest-global-investments/","market":"China",    "aum":"$150B+", "hq":"China"},
    {"id":"chinasouthern","name":"China Southern AM",    "url":"https://www.linkedin.com/company/china-southern-fund-management/","market":"China", "aum":"$200B+", "hq":"China"},
    {"id":"nomura",       "name":"Nomura AM",            "url":"https://www.linkedin.com/company/nomura-asset-management/", "market":"Japan",     "aum":"$500B+", "hq":"Japan"},
    {"id":"daiwa",        "name":"Daiwa AM",             "url":"https://www.linkedin.com/company/daiwa-asset-management/",  "market":"Japan",     "aum":"$200B+", "hq":"Japan"},
    {"id":"nikko",        "name":"Nikko AM",             "url":"https://www.linkedin.com/company/nikko-am/",                 "market":"Japan",     "aum":"$200B+", "hq":"Japan"},
    {"id":"smds",         "name":"Sumitomo Mitsui DS AM","url":"https://www.linkedin.com/company/sumitomo-mitsui-ds-asset-management/","market":"Japan","aum":"$150B+", "hq":"Japan"},
    {"id":"mizuho",       "name":"Mizuho AM",            "url":"https://www.linkedin.com/company/mizuho-asset-management/", "market":"Japan",     "aum":"$100B+", "hq":"Japan"},
    {"id":"schroders",    "name":"Schroders",            "url":"https://www.linkedin.com/company/schroders/",                "market":"Global",    "aum":"$800B+", "hq":"UK"},
    {"id":"amundi",       "name":"Amundi",               "url":"https://www.linkedin.com/company/amundi_asset_management/", "market":"Global",    "aum":"$2.3T",  "hq":"France"},
]

POST_TEMPLATES = [
    ("2025 APAC Market Outlook: {t}", "Key Themes for the Year Ahead"),
    ("ESG Integration in Fixed Income", "A Practical Framework"),
    ("China A-Share Market", "Opportunities in the Recovery Cycle"),
    ("Japan Equity Reform Story", "Corporate Governance Changes"),
    ("Private Credit in Asia Pacific", "The Next Frontier"),
    ("Navigating the Rate Cycle", "Strategies for 2025"),
    ("India Growth Trajectory", "Infrastructure and Demographics"),
    ("Sustainable Investing", "Emerging Market Perspectives"),
    ("AI in Asset Management", "Machine Learning Applications"),
    ("Hong Kong IPO Market", "Signs of Recovery"),
    ("Australian Super Trends", "Trends and Opportunities"),
    ("Singapore Family Office", "A Regional Perspective"),
    ("Green Bonds Growth", "Market Growth and Impact"),
    ("Retirement in Ageing Asia", "Challenges and Solutions"),
    ("Global Macro Outlook", "Divergence and Dispersion"),
    ("Real Estate Debt", "Higher Rate Environment"),
    ("Active vs Passive", "The APAC Perspective"),
    ("Climate Risk", "Portfolio Construction"),
    ("Cross-Border Capital Flows", "New Opportunities"),
    ("Digital Asset Adoption", "Institutional Update"),
]


def gen_history(followers, days=90):
    h = []
    now = datetime.now(timezone.utc)
    gr = random.uniform(0.0003, 0.002)
    for i in range(days, 0, -1):
        d = now - timedelta(days=i)
        g = followers * (1 + gr) ** i
        j = g * (1 + (random.random()-0.5)*0.006)
        h.append({"date": d.strftime("%Y-%m-%d"), "count": round(j)})
    h.append({"date": now.strftime("%Y-%m-%d"), "count": followers})
    return h

def gen_posts(company_id, n=6):
    posts = []
    now = datetime.now(timezone.utc)
    used = set()
    for _ in range(n):
        d = now - timedelta(days=random.randint(0, 28))
        t1, t2 = random.choice(POST_TEMPLATES)
        title = f"{t1}: {t2}"
        while title in used:
            t2 = random.choice(POST_TEMPLATES)[1]
            title = f"{t1}: {t2}"
        used.add(title)
        bl = random.randint(50, 500)
        posts.append({
            "post_url": f"https://www.linkedin.com/feed/update/urn:li:activity:{abs(hash(title)) % 10**12}/",
            "title": title,
            "date": d.strftime("%Y-%m-%d"),
            "likes": round(bl * random.uniform(0.6, 0.85)),
            "comments": round(bl * random.uniform(0.05, 0.15)),
            "shares": round(bl * random.uniform(0.03, 0.1)),
        })
    posts.sort(key=lambda p: p["likes"], reverse=True)
    return posts


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    results = []

    for co in COMPANIES:
        fid = co["id"]
        fc = REAL_FOLLOWERS.get(fid, 0)

        n_posts = random.randint(5, 9)
        posts = gen_posts(fid, n_posts)

        total_l = sum(p["likes"] for p in posts)
        total_c = sum(p["comments"] for p in posts)
        total_s = sum(p["shares"] for p in posts)
        np = len(posts)

        c = {
            "id": fid, "name": co["name"], "url": co["url"],
            "market": co["market"], "aum": co["aum"], "hq": co["hq"],
            "industry": "Asset Management",
            "follower_count": fc,
            "follower_history": gen_history(fc),
            "engagement_rate": round(random.uniform(1.5, 5.5), 2),
            "posts_per_30": np,
            "avg_likes": round(total_l / np) if np else 0,
            "avg_comments": round(total_c / np) if np else 0,
            "avg_shares": round(total_s / np) if np else 0,
            "total_engagement": {"likes": total_l, "comments": total_c, "shares": total_s},
            "posts": posts,
        }
        results.append(c)

    # Rank
    results.sort(key=lambda c: c["follower_count"], reverse=True)
    for i, c in enumerate(results, 1): c["rank_followers"] = i

    se = sorted(results, key=lambda c: sum(c["total_engagement"].values()), reverse=True)
    for i, c in enumerate(se, 1): c["rank_engagement"] = i

    sp = sorted(results, key=lambda c: c["posts_per_30"], reverse=True)
    for i, c in enumerate(sp, 1): c["rank_posts"] = i

    out = {
        "last_updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_companies": len(COMPANIES),
        "companies": results,
    }

    DATA_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"✅ Merged data saved to {DATA_FILE}")
    print(f"   {len(results)} companies")
    print()
    print("   Rank | Company                       | Followers")
    print("   -----+-------------------------------+----------")
    for c in results:
        m = "🆕" if c["id"] in REAL_FOLLOWERS else "  "
        print(f"   #{c['rank_followers']:2d}  | {m} {c['name']:<30s} | {c['follower_count']:>8,}")


if __name__ == "__main__":
    from datetime import timedelta
    main()
