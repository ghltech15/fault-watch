# ⚠️ FAULT.WATCH

**Adaptive Systemic Risk Intelligence Platform**

Real-time monitoring of the Morgan Stanley silver short position crisis, bank exposure tracking, and Federal Reserve response analysis.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.40-red.svg)

---

## 🚨 What This Tracks

- **Morgan Stanley** rumored 5.9 billion oz silver short position
- **SEC Deadline** countdown (February 15, 2026)
- **Bank PM Derivatives** exposure (JPM $437B, Citi $204B)
- **Federal Reserve** emergency repo operations
- **Domino Effect** cascade tracking
- **Your Positions** P&L calculator

---

## 📊 Live Dashboard

**Production:** [https://fault-watch.fly.dev](https://fault-watch.fly.dev)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | Python 3.11 |
| Database | Supabase (PostgreSQL) |
| Hosting | Fly.io |
| CI/CD | GitHub Actions |
| Data | Yahoo Finance, CoinGecko |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Git

### Setup

```bash
# Clone the repo
git clone https://github.com/aitechconsultants/fault-watch.git
cd fault-watch

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run fault_watch.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🗄️ Database Setup (Supabase)

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to SQL Editor
4. Run `supabase_schema.sql`
5. Copy your API keys to `.env`

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

---

## 🚀 Deploy to Production (Fly.io)

### First Time Setup

```bash
# Install Fly CLI (Windows PowerShell)
irm https://fly.io/install.ps1 | iex

# Login
flyctl auth login

# Launch app (first time)
flyctl launch

# Deploy
flyctl deploy
```

### Automatic Deployments

Push to `main` branch → GitHub Actions → Auto-deploy to Fly.io

```bash
git add .
git commit -m "Update dashboard"
git push origin main
# 🚀 Automatically deploys!
```

---

## 🔑 Environment Variables

Set these in Fly.io:

```bash
flyctl secrets set SUPABASE_URL=https://xxx.supabase.co
flyctl secrets set SUPABASE_KEY=your-anon-key
```

---

## 📁 Project Structure

```
fault-watch/
├── .github/
│   └── workflows/
│       └── deploy.yml      # CI/CD pipeline
├── fault_watch.py          # Main Streamlit app
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container config
├── fly.toml               # Fly.io config
├── supabase_schema.sql    # Database schema
├── .env.example           # Environment template
├── .gitignore
└── README.md
```

---

## 📈 Dashboard Tabs

| Tab | Description |
|-----|-------------|
| 📊 Dashboard | Main overview, scenarios, real-time prices |
| 🏦 MS Collapse | Countdown timer, stress meter, losses |
| 💀 Bank Exposure | All at-risk banks, PM derivatives data |
| 🏛️ Fed Response | Emergency lending tracker, bailout comparison |
| 🎯 Dominoes | Cascade effect tracker (8 dominoes) |
| 💰 Positions | Your trades P&L calculator |
| 📈 Scenarios | Probability analysis |

---

## ⚠️ Disclaimer

**This is NOT financial advice.**

- Based on UNVERIFIED whistleblower information
- Speculative scenario analysis only
- Risk of TOTAL LOSS on any trades
- Do your own research
- Consult a financial advisor

---

## 📊 Data Sources

| Data | Source | Update Frequency |
|------|--------|------------------|
| Stock Prices | Yahoo Finance | 60 seconds |
| Crypto Prices | CoinGecko | 60 seconds |
| PM Derivatives | OCC Quarterly Reports | Quarterly |
| Fed Repo | NY Fed | Daily |

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 👤 Author

**AI Tech Consultants**
- GitHub: [@aitechconsultants](https://github.com/aitechconsultants)

---

## 🙏 Acknowledgments

- Silver community for research
- Streamlit for amazing framework
- Fly.io for free hosting
- Supabase for database

---

*Built with ☕ and paranoia about systemic risk*
