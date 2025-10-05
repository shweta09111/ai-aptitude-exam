# 🚂 RAILWAY DEPLOYMENT GUIDE - FULL FEATURES

## ✅ Prerequisites Complete
- [x] GitHub repository: `shweta09111/ai-aptitude-exam`
- [x] Railway configuration files created
- [x] Full ML requirements (torch, transformers, BERT)
- [x] All code pushed to GitHub

---

## 🚀 DEPLOYMENT STEPS (5 Minutes)

### **STEP 1: Create Railway Account**

1. Go to: **https://railway.app**
2. Click **"Login"** or **"Start a New Project"**
3. Sign up with **GitHub account**
   - Click "Login with GitHub"
   - Authorize Railway to access your repos
4. ✅ **No credit card required!** (You get $5 credit automatically)

---

### **STEP 2: Create New Project**

1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Find and select: **`shweta09111/ai-aptitude-exam`**
4. Railway will auto-detect settings:
   - ✅ Python detected
   - ✅ Procfile found
   - ✅ requirements.txt found
5. Click **"Deploy Now"**

---

### **STEP 3: Add PostgreSQL Database**

1. In your Railway project dashboard
2. Click **"+ New"** button
3. Select **"Database"** → **"Add PostgreSQL"**
4. PostgreSQL will be created automatically
5. ✅ Railway auto-connects it to your app (DATABASE_URL set)

---

### **STEP 4: Configure Environment Variables**

1. Click on your **app service** (not database)
2. Go to **"Variables"** tab
3. Add these variables:

```
SECRET_KEY = your-secret-key-here-change-this-123
FLASK_ENV = production
```

**Note:** `DATABASE_URL` is automatically set by Railway!

---

### **STEP 5: Wait for Deployment**

1. Go to **"Deployments"** tab
2. Watch the build logs:
   - ✅ Installing dependencies (~5-10 minutes for first deploy)
   - ✅ Building with torch, transformers
   - ✅ Starting gunicorn server
3. Wait for **"Success"** status

---

### **STEP 6: Get Your Live URL**

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Your app URL: `https://your-app-name.railway.app`
5. ✅ **Your app is LIVE!**

---

### **STEP 7: Initialize Database (First Time)**

1. Open your Railway app URL
2. Go to: `https://your-app-name.railway.app/init_db`
3. You should see: "Database initialized!"
4. Or run migrations if needed

---

### **STEP 8: Create Admin Account**

1. Go to: `https://your-app-name.railway.app/register`
2. Create your admin account:
   - Username: admin
   - Email: your@email.com
   - Password: (strong password)
3. Login and test!

---

## 🎉 YOU'RE LIVE!

**All Features Working:**
- ✅ User authentication
- ✅ Exam system
- ✅ PostgreSQL database
- ✅ BERT text analysis
- ✅ Transformers ML
- ✅ AI difficulty classification
- ✅ Scikit-learn models
- ✅ OpenCV proctoring (if used)
- ✅ Data visualization
- ✅ Everything!

---

## 💰 Credit Usage

**Your $5 Credit:**
- Should last **3-4 weeks** with moderate usage
- Usage shown in Railway dashboard
- When low, you'll get email notification

**After Credit Runs Out:**
- Railway will ask for payment method
- Or move to Oracle Cloud (permanent free!)

---

## 📊 Monitor Your Usage

1. **Dashboard** → **"Usage"** tab
2. See real-time:
   - vCPU usage
   - RAM usage
   - Network traffic
   - Estimated cost
3. Optimize if needed!

---

## 🔧 Common Issues & Solutions

### **Issue 1: Build Timeout**
- **Solution:** Railway has 30-min timeout (torch is large)
- Usually works on first try
- If fails, redeploy

### **Issue 2: Out of Memory**
- **Solution:** Railway gives 8GB RAM (enough!)
- Check your logs

### **Issue 3: Database Connection Error**
- **Solution:** Make sure DATABASE_URL is set
- Check PostgreSQL service is running

### **Issue 4: App Not Starting**
- **Solution:** Check logs for errors
- Verify Procfile is correct
- Check if all dependencies installed

---

## 🎯 NEXT STEPS

While using Railway (3-4 weeks):

1. ✅ Test all features
2. ✅ Add your questions
3. ✅ Invite users
4. ✅ Meanwhile, set up Oracle Cloud (permanent free)
5. ✅ Migrate before credit runs out

---

## 📞 Need Help?

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

**Your GitHub:** Already setup and ready!

---

## 🚀 ORACLE CLOUD SETUP (Coming Next)

While Railway is running, I'll help you set up Oracle Cloud for permanent FREE hosting with all features!

**Estimated Setup Time:** 60 minutes
**Cost:** $0 forever
**Benefits:** Keep all features without paying

---

**Ready? Go to https://railway.app and start deploying!** 🎉

You have everything configured and ready to go!
