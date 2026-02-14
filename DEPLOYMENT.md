# Streamlit Cloud Deployment Guide

This guide walks you through deploying the Market Regime Detection System to Streamlit Cloud.

---

## 🚀 Quick Deployment (5 Minutes)

### Prerequisites
- ✅ GitHub repository: `shamiquekhan/Market-Regime-Detection-System` (already pushed)
- ✅ Streamlit Cloud account (free) - Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)

---

## Step-by-Step Deployment

### 1. Sign in to Streamlit Cloud

1. Go to **https://streamlit.io/cloud**
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit Cloud to access your GitHub repositories

### 2. Create New App

1. Click **"New app"** button
2. Fill in the deployment form:

   ```
   Repository: shamiquekhan/Market-Regime-Detection-System
   Branch: main
   Main file path: app/app.py
   ```

3. Click **"Advanced settings"** (optional but recommended):

   **Python version:** `3.11`
   
   **Secrets:** (if needed later for API keys)
   ```toml
   # Add any API keys or sensitive data here
   # Example:
   # API_KEY = "your-api-key"
   ```

4. Click **"Deploy!"**

### 3. Wait for Deployment

Streamlit Cloud will:
- ✅ Clone your repository
- ✅ Install dependencies from `requirements.txt`
- ✅ Build and launch your app
- ✅ Provide a public URL (e.g., `https://shamiquekhan-market-regime-detection.streamlit.app`)

**Deployment time:** 2-5 minutes

---

## 📱 Your App URL

After deployment, your app will be live at:

```
https://shamiquekhan-market-regime-detection-system.streamlit.app
```

Or similar (Streamlit auto-generates the URL based on your GitHub username and repo name)

You can find the exact URL in the Streamlit Cloud dashboard.

---

## ⚙️ Configuration

### Application Settings (Already Configured)

Your repository includes:
- ✅ `.streamlit/config.toml` - UI theme (Swiss minimalist design)
- ✅ `requirements.txt` - All Python dependencies
- ✅ `app/app.py` - Main application entry point

### Memory & Resources

**Default Resources:**
- CPU: 0.078 cores
- Memory: 800 MB

**If you need more:**
- Upgrade to Streamlit Cloud Pro for larger datasets
- Or optimize data caching in the app

---

## 🔄 Auto-Deployment

Every time you push changes to GitHub `main` branch, Streamlit Cloud will:
1. Detect the changes
2. Automatically rebuild and redeploy your app
3. Update the live site (takes 2-5 minutes)

**To deploy updates:**
```bash
# Make your changes locally
git add .
git commit -m "Your update message"
git push origin main
# Wait 2-5 minutes, then refresh your Streamlit app URL
```

---

## 🐛 Troubleshooting

### Issue: App won't start

**Check deployment logs:**
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. View **"Logs"** tab
4. Look for error messages

**Common fixes:**
- Ensure `requirements.txt` is in the root directory ✅
- Verify `app/app.py` path is correct ✅
- Check Python version compatibility (3.9-3.11) ✅

### Issue: Dependencies fail to install

**Solution:**
- Check for incompatible package versions
- Add version constraints if needed (already using `>=`)

### Issue: App runs out of memory

**Solutions:**
1. Reduce date range (load less data)
2. Optimize caching with `@st.cache_data`
3. Use smaller feature sets
4. Upgrade to Streamlit Cloud Pro

### Issue: Slow data loading

**Solutions:**
- Implement data caching (already in app)
- Use `@st.cache_data` decorator on expensive functions
- Limit historical data range to 3-5 years max

---

## 📊 Performance Optimization

### For Streamlit Cloud Deployment

**Recommended settings in sidebar:**
```python
# Optimal for free tier:
Date Range: 2020-2024 (4 years max)
Index: NIFTY50
Model: HMM (faster than GMM for deployment)
Regimes: 4 (optimal)
```

**Why:**
- 4 years of daily data = ~1,000 rows (manageable for 800MB memory)
- HMM with 4 states trains in 5-10 seconds
- Feature computation is fast with vectorized operations

### Caching Strategy

Already implemented in `app/app.py`:
```python
@st.cache_data
def load_and_process_data(symbol, start, end):
    # Cached data loading
    pass
```

This ensures data is only downloaded once per session.

---

## 🔒 Security & Privacy

### Data Privacy
- ✅ All data fetched from public Yahoo Finance API
- ✅ No user data stored
- ✅ No authentication required

### API Rate Limits
**Yahoo Finance:**
- Free tier: ~2,000 requests/hour
- Each app user triggers 1 request per data load
- Caching prevents repeated requests

**If you hit limits:**
- Add `time.sleep(1)` between requests
- Implement request throttling
- Consider premium data provider (NSE API)

---

## 🎨 Custom Domain (Optional)

Streamlit Cloud allows custom domains on Pro plan:

1. Go to **App settings** → **General**
2. Add your custom domain (e.g., `regimes.shamiquekhan.com`)
3. Update DNS records as instructed
4. SSL certificate auto-provisioned

---

## 📈 Monitoring & Analytics

### Built-in Metrics (Streamlit Cloud Dashboard)

- **App views:** Number of users
- **Uptime:** % time app is available
- **Errors:** Runtime exceptions
- **Resource usage:** CPU & memory

### Custom Analytics (Optional)

Add to `app/app.py`:
```python
import streamlit as st

# Track page views
if 'visits' not in st.session_state:
    st.session_state.visits = 0
st.session_state.visits += 1

# Display in footer
st.sidebar.metric("Total Visits", st.session_state.visits)
```

---

## 💰 Pricing

### Free Tier (Current Setup)
- ✅ 1 private app OR unlimited public apps
- ✅ 800 MB memory
- ✅ Auto-deployment from GitHub
- ✅ Community support
- **Cost:** $0/month

### Pro Tier (If Needed)
- ✅ Unlimited private apps
- ✅ 2.6 GB memory
- ✅ Priority support
- ✅ Custom domains
- **Cost:** $20/month per user

**Recommendation:** Start with free tier. Upgrade only if you need more memory or privacy.

---

## 📱 Share Your App

Once deployed, share your app:

**Direct Link:**
```
https://shamiquekhan-market-regime-detection-system.streamlit.app
```

**Embed in Website:**
```html
<iframe src="https://shamiquekhan-market-regime-detection-system.streamlit.app" 
        width="100%" height="800px" frameborder="0"></iframe>
```

**Social Media:**
- LinkedIn: "Just deployed my Market Regime Detection System using HMM/GMM models for NIFTY50 analysis. Try it live: [link]"
- Twitter: "🚀 Deployed ML-powered regime detection for Indian stock market. Sharpe 1.35, Calmar 0.62 on NIFTY50. Live demo: [link]"

---

## 🔄 Updating Your Deployed App

### Method 1: Push to GitHub (Recommended)
```bash
# Make changes locally
git add .
git commit -m "Update: Added new feature"
git push origin main
# App auto-updates in 2-5 minutes
```

### Method 2: Reboot from Dashboard
1. Go to Streamlit Cloud dashboard
2. Click **"⋮"** menu on your app
3. Select **"Reboot app"**
4. Waits for latest GitHub commit

---

## 🎯 Post-Deployment Checklist

After successful deployment:

- [ ] Test app at live URL
- [ ] Verify all features work (data loading, model training, charts)
- [ ] Check evaluation metrics display correctly
- [ ] Test CSV export functionality
- [ ] Add app URL to GitHub repository description
- [ ] Add app URL to README.md
- [ ] Share on social media
- [ ] Monitor logs for first 24 hours

---

## 🆘 Support

**Streamlit Cloud Issues:**
- Documentation: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io
- Email: support@streamlit.io

**App-Specific Issues:**
- GitHub Issues: https://github.com/shamiquekhan/Market-Regime-Detection-System/issues
- Email: shamiquekhan@example.com

---

## 🎉 Success!

Your Market Regime Detection System is now live and accessible to anyone worldwide!

**Next Steps:**
1. Share your app URL with traders/analysts
2. Gather user feedback
3. Implement Phase 1 deployment (paper trading) per IMPLEMENTATION_ROADMAP.md
4. Monitor performance and iterate

**Happy Trading! 📈**

---

**Last Updated:** February 14, 2026  
**Version:** 1.0.1  
**Deployment Platform:** Streamlit Cloud (Free Tier)
