# LinkedIn Social Listening Dashboard
# APAC Asset Management Company Tracker

## Project Directory
`C:\Hermes\linkedin-tracker\`

```
linkedin-tracker/
├── research/
│   ├── apac_asset_managers.csv    # 30 companies with LinkedIn URLs
│   └── metrics.md                 # Social listening metrics reference
├── scraper/
│   ├── linkedin_scraper.py        # Scrapling-based LinkedIn scraper
│   └── requirements.txt           # Python dependencies
├── dashboard/
│   ├── index.html                 # Main dashboard (TradingView-style)
│   ├── css/
│   │   └── dashboard.css          # Dark theme styles
│   └── js/
│       └── dashboard.js           # Interactive dashboard logic
├── data/
│   └── companies.json             # Scraped data cache
└── .github/workflows/
    └── update_data.yml            # GitHub Actions scheduled scrape
```

## Deployment
- GitHub repo: `dancingturtle14/linkedin-tracker`
- GitHub Pages: `dancingturtle14.github.io/linkedin-tracker/`

## Tech Stack
| Component | Tool | Purpose |
|-----------|------|---------|
| Scraper | D4Vinci/Scrapling | LinkedIn company page scraping (StealthyFetcher bypasses Cloudflare) |
| Data Format | JSON/CSV | Company page stats + post metrics |
| Automation | GitHub Actions | Cron-based daily/weekly scrape |
| Frontend | Vanilla JS + CSS | TradingView-style dark dashboard |
| Charting | Chart.js | Interactive charts |

## Focus Markets (7 markets)
| Market | Companies |
|--------|-----------|
| 🌏 Global | J.P. Morgan AM, BlackRock, Fidelity |
| 🇭🇰 Hong Kong | HSBC Asset Management |
| 🇸🇬 Singapore | Eastspring Investments |
| 🇦🇺 Australia | Macquarie AM, First Sentier, AMP Capital |
| 🇨🇳 China | Ping An AM, China AMC, E Fund, Harvest, China Southern AM |
| 🇯🇵 Japan | Nomura AM, Daiwa AM, Nikko AM, Sumitomo Mitsui DS AM, Mizuho AM |
| 🌐 APAC coverage | Schroders, Amundi |

## Key Firms (20 companies)
See `research/apac_asset_managers.csv` for full list.

## Social Listening Metrics Tracked
See `research/metrics.md` for full details.

8 categories:
1. Follower Metrics (growth, demographics, trends)
2. Engagement Metrics (impressions, reactions, shares, CTR)
3. Content Metrics (post frequency, topics, formats, hashtags)
4. Sentiment Analysis (positive/negative/neutral per post)
5. Competitive Benchmarking (share of voice, comparison)
6. Page-Level Performance (visitors, CTAs)
7. Conversion/ROI (lead gen, website clicks)
8. APAC-Specific (language breakdown, regulatory sentiment, ESG tracking)

## LinkedIn Scraping Strategy
- Use Scrapling StealthyFetcher with adaptive=True for Cloudflare bypass
- Fetch company page via LinkedIn public profile URL
- Extract: follower count, recent posts, engagement metrics
- Store as structured JSON in data/ directory
- GitHub Actions runs scraper daily and commits updated data

## Dashboard Layout (TradingView Inspired)
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 LinkedIn Tracker — APAC Asset Management               │
│  [Company Selector ▼]  [Metrics ▼]  [Date Range ▼]  [↻]   │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│ │ Follower     │ │ Engagement  │ │ Post        │ │ Sent   │ │
│ │ Total: 1.2M  │ │ Rate: 3.4% │ │ Frequency   │ │ Score  │ │
│ │ ▲ +2.5% wk  │ │ ▲ +0.8% wk │ │ 4.2/day     │ │ +72    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  Follower Growth Trend (30 days)                   [▼]  │ │
│ │  📈 [area chart — all companies overlay]               │ │
│ │  ━ BlackRock ━ JPMorgan ━ Nomura ━ Eastspring         │ │
│ └─────────────────────────────────────────────────────────┘ │
├──────────────┬──────────────────────────────────────────────┤
│ Companies    │ Recent Posts / Activity Feed                 │
│ List         │ ┌────────────────────────────────────────┐  │
│ [x]BlackRock │ │ BlackRock — 2h ago                     │  │
│ [x]JPMorgan  │ │ 2026 APAC Market Outlook published     │  │
│ [x]Nomura    │ │ ❤ 234 💬 45 🔄 12                      │  │
│ [x]Eastspring│ ├────────────────────────────────────────┤  │
│ [x]Amundi    │ │ Nomura AM — 5h ago                     │  │
│ [ ]Fidelity  │ │ Japan ESG Investment Trends Report     │  │
│              │ │ ❤ 89 💬 12 🔄 3                        │  │
│              │ └────────────────────────────────────────┘  │
├──────────────┴──────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│ │ Content Type │ │ Top Hashtags │ │ Sentiment by Topic   │ │
│ │ 🎬 45% Video │ │ #APAC        │ │ ESG 🟢 85%          │ │
│ │ 📝 30% Text  │ │ #AssetMgmt   │ │ China 🟡 62%        │ │
│ │ 🖼 25% Image │ │ #ESG         │ │ Rates 🔴 45%        │ │
│ └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```
