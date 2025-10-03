# Quick Internet Sharing - 2 Options

## 🚀 Option 1: ngrok (Fastest - 5 minutes)

### Step 1: Download & Install
1. Go to https://ngrok.com/download
2. Download Windows ZIP
3. Extract `ngrok.exe` to `C:\ngrok\` (or any folder)

### Step 2: Sign Up & Get Auth Token
1. Sign up free: https://dashboard.ngrok.com/signup
2. Copy your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken

### Step 3: Configure
Open PowerShell/Command Prompt:
```bash
C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN_HERE
```

### Step 4: Start Tunnel
Make sure your frontend is running, then in a NEW terminal:
```bash
C:\ngrok\ngrok.exe http 5173
```

### Step 5: Share the URL
ngrok will display:
```
Forwarding    https://abc123-xyz.ngrok-free.app -> http://localhost:5173
```

**Share this URL**: `https://abc123-xyz.ngrok-free.app`

Anyone can access it from anywhere!

**Note**:
- Free tier URL changes each time you restart ngrok
- Bandwidth limits on free tier
- Keep terminal open while sharing

---

## ☁️ Option 2: Heroku (Permanent URL - 30 minutes)

### Prerequisites
- Git installed
- Heroku account (free): https://signup.heroku.com

### Step 1: Install Heroku CLI
Download: https://devcenter.heroku.com/articles/heroku-cli

Verify installation:
```bash
heroku --version
```

### Step 2: Login
```bash
heroku login
```

### Step 3: Create Heroku App
```bash
cd texas-energy-analyzer
heroku create your-app-name
# Example: heroku create texas-energy-marcelo
```

### Step 4: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:essential-0
```

### Step 5: Set Environment Variables
```bash
# Generate secure keys
$SECRET_KEY = -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
$API_KEY = -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })

# Set them
heroku config:set SECRET_KEY=$SECRET_KEY
heroku config:set API_KEY=$API_KEY
```

### Step 6: Deploy
```bash
git add -A
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

### Step 7: Initialize Database
```bash
heroku run python backend/update_provider_websites.py
```

### Step 8: Open Your App
```bash
heroku open
```

**Your permanent URL**: `https://your-app-name.herokuapp.com`

---

## 📊 Comparison

| Feature | ngrok | Heroku |
|---------|-------|--------|
| **Setup Time** | 5 minutes | 30 minutes |
| **Cost** | Free (with limits) | Free tier available |
| **URL** | Changes each restart | Permanent |
| **Uptime** | Only when computer on | 24/7 |
| **Performance** | Depends on your PC | Cloud servers |
| **Bandwidth** | Limited (free tier) | Higher limits |
| **Database** | Your local SQLite | PostgreSQL |
| **Best For** | Quick sharing/testing | Long-term use |

---

## 🎯 My Recommendation

**For quick sharing with 1-2 friends**: Use ngrok
- Takes 5 minutes
- No deployment needed
- Perfect for showing off your project

**For sharing with many people or long-term**: Use Heroku
- Takes 30 minutes one-time setup
- URL never changes
- Always available
- More professional

---

## 🔧 Troubleshooting

### ngrok: "command not found"
Use full path:
```bash
C:\ngrok\ngrok.exe http 5173
```

Or add to PATH:
1. Search "Environment Variables" in Windows
2. Edit "Path"
3. Add `C:\ngrok\`

### Heroku: "No Procfile found"
Make sure you're in the project directory:
```bash
cd texas-energy-analyzer
```

Verify Procfile exists:
```bash
ls Procfile
```

### ngrok: "Failed to bind to localhost:5173"
Make sure frontend is running first:
```bash
cd texas-energy-analyzer/frontend
npm run dev
```

Then start ngrok in a different terminal.

---

## 💡 Quick Start Commands

### ngrok (After installation):
```bash
# Terminal 1: Start frontend
cd texas-energy-analyzer/frontend
npm run dev

# Terminal 2: Start ngrok
ngrok http 5173
```

### Heroku (One-time setup):
```bash
cd texas-energy-analyzer
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0
heroku config:set SECRET_KEY=your_secret_key
heroku config:set API_KEY=your_api_key
git push heroku main
```

---

## 📱 Share Your Link!

Once deployed, share your URL:

**ngrok**:
```
Hey! Check out my electricity plan analyzer:
https://abc123-xyz.ngrok-free.app

(Note: Link changes when I restart my computer)
```

**Heroku**:
```
Hey! Check out my electricity plan analyzer:
https://texas-energy-marcelo.herokuapp.com

Save this link - it's permanent!
```

---

## 🎉 Next Steps

After deploying:
1. Share your URL with friends
2. Test from your phone (use cellular, not WiFi)
3. Monitor usage in ngrok/Heroku dashboard
4. Add custom domain (Heroku paid tier)

Need help? Check:
- ngrok docs: https://ngrok.com/docs
- Heroku docs: https://devcenter.heroku.com
- PRODUCTION_DEPLOYMENT.md (for advanced setups)
