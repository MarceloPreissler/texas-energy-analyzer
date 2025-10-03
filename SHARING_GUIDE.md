# How to Share the Texas Energy Analyzer

## ✅ Yes, the app is shareable!

The Texas Energy Analyzer is now configured to be accessible from any device on your local network.

## 📱 Access URLs

### On Your Computer (Local)
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000

### From Other Devices (Network)
- **Frontend**: http://10.0.0.16:5173
- **Backend API**: http://10.0.0.16:8000

Replace `10.0.0.16` with your actual IP address (see below).

## 🌐 Finding Your IP Address

### Windows
```bash
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

### Mac/Linux
```bash
ifconfig
# Look for "inet" under your active network adapter
```

The frontend will also display it when you start the dev server:
```
➜  Local:   http://localhost:5173/
➜  Network: http://YOUR_IP:5173/
```

## 📲 Sharing with Friends

### Same Network (WiFi/LAN)
1. Make sure both servers are running:
   ```bash
   # Backend
   cd texas-energy-analyzer/backend
   .venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Frontend
   cd texas-energy-analyzer/frontend
   npm run dev
   ```

2. Share your network URL with friends:
   ```
   http://YOUR_IP:5173
   ```

3. Friends must be on the **same WiFi/network** as you

### Example Sharing
```
Hey! Check out the Texas Energy Analyzer I built:
http://10.0.0.16:5173

(Make sure you're on my WiFi first!)
```

## 🔒 Firewall & Security

### Windows Firewall
You may need to allow connections on ports 5173 and 8000:

1. **Open Windows Defender Firewall**
2. Click **"Allow an app through firewall"**
3. Click **"Change settings"** → **"Allow another app"**
4. Add rules for:
   - Node.js (frontend - port 5173)
   - Python (backend - port 8000)

### Quick Firewall Rule (PowerShell - Run as Admin)
```powershell
# Allow frontend
New-NetFirewallRule -DisplayName "Texas Energy Analyzer - Frontend" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow

# Allow backend
New-NetFirewallRule -DisplayName "Texas Energy Analyzer - Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

## 🚀 Internet Sharing (Advanced)

To share with people **not on your network**, you'll need one of these options:

### Option 1: Deploy to Cloud (Recommended)
Follow `PRODUCTION_DEPLOYMENT.md` to deploy to:
- **Heroku** (easiest, ~$15/month)
- **AWS** (~$42/month)
- **Azure** (~$75/month)

Then share the public URL: `https://your-app.herokuapp.com`

### Option 2: Ngrok (Quick Testing)
```bash
# Install ngrok
# https://ngrok.com/download

# Expose frontend
ngrok http 5173

# Share the ngrok URL: https://abc123.ngrok.io
```

**Note**: Free ngrok URLs change every time you restart.

### Option 3: Port Forwarding (Technical)
1. Configure port forwarding on your router
2. Forward ports 5173 and 8000 to your computer's local IP
3. Share your public IP: `http://YOUR_PUBLIC_IP:5173`

**⚠️ Security Warning**: Exposing ports publicly can be risky. Use Docker deployment with HTTPS for production.

## 🔗 Provider Website Links

Each provider name in the plan table is now a clickable link:
- **Gexa Energy** 🔗 → https://www.gexaenergy.com
- **TXU Energy** 🔗 → https://www.txu.com
- **Direct Energy** 🔗 → https://www.directenergy.com
- **Reliant Energy** 🔗 → https://www.reliant.com

Click to:
- Verify current pricing
- See full plan details
- Sign up directly with provider
- Compare with PowerToChoose.org data

## 📊 What Friends Can Do

When accessing the shared link, friends can:
- ✅ View all electricity plans
- ✅ Filter by provider, type, contract term
- ✅ Compare rates at different usage levels
- ✅ Calculate estimated monthly bills
- ✅ Select and compare up to 5 plans
- ✅ See personalized recommendations
- ✅ Click provider links to verify pricing
- ❌ Cannot trigger manual scraping (requires API key)

## 🧪 Testing

### Test Local Access
```bash
curl http://localhost:5173
curl http://localhost:8000/health
```

### Test Network Access
From another device on same network:
```bash
curl http://YOUR_IP:5173
curl http://YOUR_IP:8000/health
```

Or just open in a browser:
```
http://YOUR_IP:5173
```

## 🛠️ Troubleshooting

### "Unable to connect" Error
1. **Check servers are running**:
   ```bash
   # Should see both processes
   netstat -an | findstr "5173"
   netstat -an | findstr "8000"
   ```

2. **Check firewall** (see Firewall & Security section above)

3. **Verify same network**:
   - Both devices must be on the same WiFi/LAN
   - VPN connections may cause issues

4. **Try IP variations**:
   - If `10.0.0.16` doesn't work, try:
   - `192.168.1.X` (common home network)
   - `172.16.0.X` (some routers)

### Backend CORS Issues
Backend is configured to allow:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

If accessing from network IP, you may need to update `backend/app/main.py`:
```python
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://10.0.0.16:5173",  # Add your network IP
    "http://YOUR_IP:5173",
]
```

### Frontend Proxy Issues
If API calls fail on network access, update `frontend/vite.config.ts`:
```typescript
proxy: {
  '/plans': {
    target: 'http://YOUR_IP:8000',  // Use network IP instead of localhost
    changeOrigin: true,
  },
}
```

## 📝 Summary

**Current Setup:**
- ✅ **Local access**: Works out of the box
- ✅ **Same network**: Enabled with `host: '0.0.0.0'` in Vite config
- ❌ **Internet access**: Requires cloud deployment or ngrok

**Quick Share (Same Network):**
1. Start servers
2. Check IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
3. Share: `http://YOUR_IP:5173`
4. Ensure friend is on same WiFi

**Quick Share (Internet):**
1. Deploy to Heroku/AWS (see `PRODUCTION_DEPLOYMENT.md`)
2. Share public URL: `https://your-app.herokuapp.com`

**For Production**: Use Docker deployment with HTTPS, custom domain, and security hardening.
