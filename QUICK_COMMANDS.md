# 🚀 QUICK DEPLOYMENT COMMANDS

## 📌 **YOUR GITHUB USERNAME**
Replace `YOUR_USERNAME` in commands below with your actual GitHub username.

---

## 1️⃣ **CREATE GITHUB REPO**
1. Go to: https://github.com/new
2. Name: `ai-aptitude-exam`
3. **DON'T** initialize with README
4. Click "Create repository"

---

## 2️⃣ **CONNECT & PUSH TO GITHUB**

```powershell
# Connect to GitHub (replace YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/ai-aptitude-exam.git

# Set main branch
git branch -M main

# Push code
git push -u origin main
```

**✅ After this, your code is on GitHub!**

---

## 3️⃣ **IMPORT TO VERCEL**
1. Go to: https://vercel.com/new
2. Click "Import Git Repository"
3. Select your `ai-aptitude-exam` repo
4. **STOP! Don't deploy yet!**

---

## 4️⃣ **CREATE POSTGRESQL ON VERCEL**
1. In Vercel project (before deploying)
2. Click "Storage" tab
3. "Create Database" → "Postgres"
4. Name: `ai-aptitude-exam-db`
5. **SAVE the POSTGRES_URL shown!**

---

## 5️⃣ **MIGRATE YOUR DATA**

```powershell
# Set database URL (paste your Vercel Postgres URL)
$env:DATABASE_URL="postgres://default:xxxxx@ep-xxxxx.us-east-1.postgres.vercel-storage.com:5432/verceldb"

# Run migration (copies all 1,013 questions)
python migrate_db.py
```

**✅ Expected: "Migration completed successfully!"**

---

## 6️⃣ **SET ENVIRONMENT VARIABLES IN VERCEL**

In Vercel → Settings → Environment Variables, add:

### **DATABASE_URL**
```
Name: DATABASE_URL
Value: [your Postgres URL from step 4]
Environments: Production, Preview, Development (all 3)
```

### **SECRET_KEY**
```powershell
# Generate key first:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Then add in Vercel:
```
Name: SECRET_KEY
Value: [paste generated key]
Environments: Production, Preview, Development (all 3)
```

### **FLASK_ENV**
```
Name: FLASK_ENV
Value: production
Environments: Production
```

---

## 7️⃣ **DEPLOY!**
1. Go to "Deployments" tab in Vercel
2. Click "Deploy" (or "Redeploy" if already deployed)
3. Wait 3-5 minutes
4. **DONE! Your app is LIVE!** 🎉

---

## 🌐 **YOUR LIVE URL**

```
https://ai-aptitude-exam-YOUR-USERNAME.vercel.app
```

Or check Vercel dashboard for exact URL.

---

## ✅ **VERIFY DEPLOYMENT**

### **Test 1: Homepage**
Visit your Vercel URL
**Expected:** Purple gradient homepage loads

### **Test 2: Login**
Go to `/login`
- Username: `admin`
- Password: `admin123`

**Expected:** Login successful, redirect to dashboard

### **Test 3: Questions**
Go to `/exam`
**Expected:** Questions load (all 1,013 available)

### **Test 4: Submit Exam**
Take a test, submit answers
**Expected:** Results save and display

---

## 🆘 **TROUBLESHOOTING**

### **Problem: Build fails**
**Check:** Vercel build logs for errors
**Fix:** Verify environment variables set

### **Problem: No questions**
**Fix:** Re-run migration:
```powershell
$env:DATABASE_URL="your-url"
python migrate_db.py
```

### **Problem: 500 error**
**Check:** Vercel Function Logs
**Common cause:** DATABASE_URL not set

---

## 🔄 **UPDATE & REDEPLOY**

When you make changes:

```powershell
# Add changes
git add .

# Commit
git commit -m "Update description"

# Push to GitHub
git push origin main

# Vercel auto-deploys! ✨
```

---

## 🔐 **IMPORTANT: After First Deployment**

1. **Change admin password!**
   - Login with admin/admin123
   - Go to settings
   - Change password

2. **Verify all features work**
   - Test exam submission
   - Check admin dashboard
   - Verify analytics

---

## 📊 **DEPLOYMENT STATUS**

- [x] ✅ Git initialized
- [x] ✅ Files committed
- [ ] Create GitHub repository
- [ ] Push to GitHub
- [ ] Import to Vercel
- [ ] Create PostgreSQL
- [ ] Migrate data
- [ ] Set environment variables
- [ ] Deploy!

---

## 🎯 **TOTAL TIME: ~15 MINUTES**

**You're almost there!** 🚀

---

*Quick Reference Guide*
*Last Updated: October 5, 2025*
