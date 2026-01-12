# 🚀 FAULT.WATCH - Complete Setup Guide

## Step-by-Step: Local Dev → GitHub → Supabase → Fly.io

---

## PHASE 1: GitHub Setup (10 minutes)

### Step 1.1: Create the Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `fault-watch`
3. Description: `Adaptive Systemic Risk Intelligence Platform`
4. Select: **Public** (or Private if you prefer)
5. Check: **Add a README file** (we'll replace it)
6. Click **Create repository**

### Step 1.2: Clone to Your Computer

Open PowerShell:

```powershell
cd C:\Users\ghlte\projects

# Clone your new repo
git clone https://github.com/aitechconsultants/fault-watch.git

cd fault-watch
```

### Step 1.3: Copy Project Files

Copy all the files from this project into your `fault-watch` folder:
- `fault_watch.py`
- `requirements.txt`
- `Dockerfile`
- `fly.toml`
- `.gitignore`
- `.env.example`
- `supabase_schema.sql`
- `README.md`
- `LICENSE`
- `setup.bat`
- `.github/workflows/deploy.yml`

### Step 1.4: Initial Commit

```powershell
git add .
git commit -m "Initial commit - fault.watch v4.0"
git push origin main
```

✅ **GitHub is now set up!**

---

## PHASE 2: Supabase Setup (15 minutes)

### Step 2.1: Create Account

1. Go to [supabase.com](https://supabase.com)
2. Click **Start your project**
3. Sign up with GitHub (easiest)

### Step 2.2: Create New Project

1. Click **New Project**
2. Organization: Create one or select existing
3. Project name: `fault-watch`
4. Database password: Generate a strong one (SAVE THIS!)
5. Region: `West US (North California)` or closest to you
6. Click **Create new project**
7. Wait 2-3 minutes for setup

### Step 2.3: Get Your API Keys

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGc...` (long string)
   - **service_role key**: `eyJhbGc...` (keep secret!)

### Step 2.4: Run Database Schema

1. Go to **SQL Editor** (left sidebar)
2. Click **New query**
3. Paste entire contents of `supabase_schema.sql`
4. Click **Run** (or Ctrl+Enter)
5. Should see "Success. No rows returned"

### Step 2.5: Enable Realtime (Optional but Recommended)

1. Go to **Database** → **Replication**
2. Find `current_prices` table
3. Toggle ON for realtime updates

✅ **Supabase is now set up!**

---

## PHASE 3: Local Development (5 minutes)

### Step 3.1: Setup Environment

```powershell
cd C:\Users\ghlte\projects\fault-watch

# Run setup script
.\setup.bat
```

Or manually:

```powershell
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3.2: Configure Environment Variables

1. Copy `.env.example` to `.env`
2. Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### Step 3.3: Run Locally

```powershell
streamlit run fault_watch.py
```

Open [http://localhost:8501](http://localhost:8501)

✅ **Local development is working!**

---

## PHASE 4: Fly.io Deployment (15 minutes)

### Step 4.1: Create Account

1. Go to [fly.io](https://fly.io)
2. Click **Get Started**
3. Sign up (can use GitHub)

### Step 4.2: Install Fly CLI

Open PowerShell as Administrator:

```powershell
irm https://fly.io/install.ps1 | iex
```

Close and reopen PowerShell, then:

```powershell
# Verify installation
flyctl version

# Login
flyctl auth login
```

### Step 4.3: Launch Your App

```powershell
cd C:\Users\ghlte\projects\fault-watch

# Launch (first time only)
flyctl launch
```

When prompted:
- App name: `fault-watch` (or accept generated name)
- Region: `sea` (Seattle) or closest to you
- PostgreSQL: **No** (we use Supabase)
- Redis: **No**
- Deploy now: **Yes**

### Step 4.4: Set Environment Secrets

```powershell
flyctl secrets set SUPABASE_URL=https://your-project.supabase.co
flyctl secrets set SUPABASE_KEY=your-anon-key-here
```

### Step 4.5: Deploy

```powershell
flyctl deploy
```

Wait 2-5 minutes. When done:

```powershell
flyctl open
```

This opens your live app at `https://fault-watch.fly.dev`

✅ **Fly.io deployment complete!**

---

## PHASE 5: GitHub Actions CI/CD (10 minutes)

### Step 5.1: Get Fly.io API Token

```powershell
flyctl tokens create deploy
```

Copy the token that appears.

### Step 5.2: Add Secret to GitHub

1. Go to your repo: `github.com/aitechconsultants/fault-watch`
2. Click **Settings** (tab)
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `FLY_API_TOKEN`
6. Value: Paste the token from Step 5.1
7. Click **Add secret**

### Step 5.3: Test Auto-Deploy

Make a small change to your code:

```powershell
# Edit fault_watch.py (change version number or something)
git add .
git commit -m "Test auto-deploy"
git push origin main
```

Go to **Actions** tab in GitHub to watch the deployment!

✅ **CI/CD is now set up!**

---

## PHASE 6: Custom Domain (Optional)

### Step 6.1: Add Domain to Fly.io

```powershell
flyctl certs create fault.watch
flyctl certs create www.fault.watch
```

### Step 6.2: Configure DNS

Add these DNS records at your domain registrar:

| Type | Name | Value |
|------|------|-------|
| A | @ | (IP from `flyctl ips list`) |
| AAAA | @ | (IPv6 from `flyctl ips list`) |
| CNAME | www | fault-watch.fly.dev |

Wait 5-30 minutes for DNS propagation.

### Step 6.3: Verify

```powershell
flyctl certs show fault.watch
```

✅ **Custom domain configured!**

---

## 🎉 YOU'RE DONE!

### Your Setup:

| Component | URL/Location |
|-----------|--------------|
| **Code** | github.com/aitechconsultants/fault-watch |
| **Database** | supabase.com (your project) |
| **Live App** | https://fault-watch.fly.dev |
| **Custom Domain** | https://fault.watch (if configured) |

### Workflow Now:

```
Edit code locally
      ↓
git push origin main
      ↓
GitHub Actions runs tests
      ↓
Auto-deploys to Fly.io
      ↓
Live in ~2 minutes!
```

---

## 🆘 Troubleshooting

### "flyctl not found"
- Restart PowerShell after installing
- Try: `$env:Path += ";$HOME\.fly\bin"`

### "Deploy failed"
- Check logs: `flyctl logs`
- Check status: `flyctl status`

### "Supabase connection failed"
- Verify your `.env` credentials
- Check Supabase dashboard is running
- Verify RLS policies allow access

### "GitHub Actions failed"
- Check the Actions tab for error logs
- Verify `FLY_API_TOKEN` secret is set correctly

---

## 📞 Support

- GitHub Issues: Open an issue in your repo
- Fly.io Docs: [fly.io/docs](https://fly.io/docs)
- Supabase Docs: [supabase.com/docs](https://supabase.com/docs)
- Streamlit Docs: [docs.streamlit.io](https://docs.streamlit.io)
