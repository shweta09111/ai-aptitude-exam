# 🚀 VERCEL DEPLOYMENT - STEP BY STEP

## 📋 **PREREQUISITES CHECKLIST**

Before deploying, make sure you have:
- [x] ✅ Vercel account (you mentioned you have one)
- [ ] GitHub account
- [ ] Git installed on your computer
- [ ] Vercel CLI (optional, can deploy via dashboard)

---

## 🎯 **DEPLOYMENT METHOD: VERCEL DASHBOARD (EASIEST)**

We'll use the Vercel Dashboard method - no CLI needed!

---

## 📦 **STEP 1: PREPARE YOUR PROJECT**

### **1.1 Initialize Git Repository**

```powershell
# Navigate to your project
cd C:\Users\Admin\ai_aptitude_exam\project

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - AI Aptitude Exam System with PostgreSQL support"
```

### **1.2 Create .gitignore**

Already checking if one exists...

---

## 🌐 **STEP 2: PUSH TO GITHUB**

### **2.1 Create New Repository on GitHub**

1. Go to https://github.com
2. Click the "+" icon → "New repository"
3. Repository name: `ai-aptitude-exam` (or your choice)
4. Description: "AI-Powered Aptitude Examination System"
5. Choose "Private" or "Public"
6. **DO NOT** initialize with README (we already have code)
7. Click "Create repository"

### **2.2 Connect Local to GitHub**

GitHub will show you commands. Use these:

```powershell
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/ai-aptitude-exam.git

# Push code
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## 🎨 **STEP 3: CREATE POSTGRESQL DATABASE ON VERCEL**

### **3.1 Go to Vercel Dashboard**

1. Visit: https://vercel.com/dashboard
2. Login with your account

### **3.2 Create New Project**

1. Click "Add New..." → "Project"
2. Click "Import Git Repository"
3. Find your `ai-aptitude-exam` repository
4. Click "Import"
5. **WAIT! Don't click Deploy yet!**

### **3.3 Add PostgreSQL Database**

**BEFORE deploying, add database:**

1. In your project settings (before first deploy)
2. Or create project first, then:
   - Go to your project
   - Click "Storage" tab
   - Click "Create Database"
   - Select "Postgres"
   - Name: `ai-aptitude-exam-db`
   - Region: Choose closest to you
   - Click "Create"

### **3.4 Get Database Connection String**

1. After database is created
2. Go to "Storage" → Your PostgreSQL database
3. Copy the `.env.local` tab content
4. You'll see `POSTGRES_URL` - **SAVE THIS!**

Example format:
```
postgres://default:abc123@ep-cool-name.us-east-1.postgres.vercel-storage.com:5432/verceldb
```

---

## 📊 **STEP 4: MIGRATE YOUR DATA TO POSTGRESQL**

### **4.1 Set Database URL Locally**

```powershell
# Set the environment variable
$env:DATABASE_URL="your-postgres-url-from-vercel"
```

Replace with your actual URL from Step 3.4

### **4.2 Run Migration Script**

```powershell
# This copies all 1,013 questions from SQLite to PostgreSQL
python migrate_db.py
```

**Expected output:**
```
🔄 Starting migration from SQLite to PostgreSQL...
📊 Found 14 tables to migrate
📋 Migrating table: users
  ✅ Table created
  ✅ Migrated 77 rows
📋 Migrating table: question
  ✅ Table created
  ✅ Migrated 1013 rows
...
✅ Migration completed successfully!
```

---

## ⚙️ **STEP 5: CONFIGURE ENVIRONMENT VARIABLES**

### **5.1 Go to Project Settings**

1. Vercel Dashboard → Your Project
2. Click "Settings" tab
3. Click "Environment Variables"

### **5.2 Add These Variables**

Add the following (click "Add" for each):

#### **DATABASE_URL**
```
Name: DATABASE_URL
Value: [paste your postgres URL from Step 3.4]
Environment: Production, Preview, Development (select all 3)
```

#### **POSTGRES_URL** (Vercel auto-adds this, but verify)
```
Name: POSTGRES_URL
Value: [same postgres URL]
Environment: Production, Preview, Development
```

#### **SECRET_KEY** (IMPORTANT!)
```
Name: SECRET_KEY
Value: [generate new random key - see below]
Environment: Production, Preview, Development
```

**Generate SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and use as SECRET_KEY value.

#### **FLASK_ENV**
```
Name: FLASK_ENV
Value: production
Environment: Production
```

#### **SESSION_COOKIE_SECURE**
```
Name: SESSION_COOKIE_SECURE
Value: true
Environment: Production
```

### **5.3 Save All Variables**

Click "Save" after adding each variable.

---

## 🚀 **STEP 6: DEPLOY TO VERCEL**

### **6.1 Trigger Deployment**

If you haven't deployed yet:
1. Go to "Deployments" tab
2. Click "Deploy"

If you already clicked deploy earlier:
1. Go to "Deployments" tab
2. Click the three dots on latest deployment
3. Click "Redeploy"

### **6.2 Watch Build Process**

1. Click on the building deployment
2. Watch the build logs
3. Wait for "Building..." → "Completed"
4. Should take 3-5 minutes

### **6.3 Get Your Live URL**

After successful deployment:
```
Your app is live at:
https://ai-aptitude-exam-YOUR-USERNAME.vercel.app
```

---

## ✅ **STEP 7: VERIFY DEPLOYMENT**

### **7.1 Test Homepage**

Visit: `https://your-project.vercel.app`

**Expected:** Homepage loads with purple gradient theme

### **7.2 Test Login**

1. Go to: `https://your-project.vercel.app/login`
2. Username: `admin`
3. Password: `admin123`
4. Click "Login"

**Expected:** Successful login, redirect to admin dashboard

### **7.3 Test Questions**

1. Go to exam page
2. Check if questions load

**Expected:** All 1,013 questions available from PostgreSQL

### **7.4 Test Exam Submission**

1. Take a test exam
2. Submit answers
3. Check results page

**Expected:** Results save to PostgreSQL and display correctly

### **7.5 Test Admin Panel**

1. Go to: `https://your-project.vercel.app/admin/dashboard`
2. Check statistics
3. Verify question count shows 1,013

**Expected:** All admin features working

---

## 🔧 **TROUBLESHOOTING**

### **Issue: Build Failed**

**Check Vercel build logs:**
1. Deployments → Click failed deployment
2. Look for error messages

**Common fixes:**
- Missing environment variables
- Check requirements_vercel.txt is used
- Verify all files committed to GitHub

### **Issue: "Internal Server Error" (500)**

**Solution:**
1. Check Vercel Function Logs:
   - Deployment → Runtime Logs
2. Look for Python errors
3. Common causes:
   - DATABASE_URL not set
   - Migration not completed
   - Missing SECRET_KEY

### **Issue: "No questions found"**

**Solution:**
```powershell
# Re-run migration
$env:DATABASE_URL="your-postgres-url"
python migrate_db.py
```

### **Issue: Login doesn't work**

**Solution:**
1. Check SECRET_KEY is set in Vercel
2. Verify admin user exists in PostgreSQL
3. Check session cookies are enabled

---

## 🔐 **SECURITY: CHANGE ADMIN PASSWORD**

### **IMPORTANT: After deployment**

1. Login as admin (admin/admin123)
2. Go to settings/profile
3. **Change password immediately!**
4. Use a strong password

---

## 📊 **MONITORING YOUR APP**

### **View Logs:**
```
Vercel Dashboard → Your Project → Deployments
→ Click deployment → View Function Logs
```

### **View Analytics:**
```
Vercel Dashboard → Your Project → Analytics
```

### **View Database:**
```
Vercel Dashboard → Storage → Your PostgreSQL DB
→ Data tab (view tables and data)
```

---

## 🎉 **SUCCESS INDICATORS**

Your deployment is successful when:

✅ Build completes without errors
✅ Homepage loads at your Vercel URL
✅ Admin can login (admin/admin123)
✅ Questions load (1,013 available)
✅ Exams can be submitted
✅ Results save to database
✅ Admin dashboard shows correct statistics
✅ No errors in Vercel logs

---

## 📝 **QUICK COMMAND REFERENCE**

```powershell
# Initialize and push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/REPO.git
git branch -M main
git push -u origin main

# Migrate data to PostgreSQL
$env:DATABASE_URL="your-postgres-url"
python migrate_db.py

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update code and redeploy
git add .
git commit -m "Update description"
git push origin main
# Vercel auto-deploys!
```

---

## 🚀 **YOU'RE READY!**

Follow each step carefully and you'll be live on Vercel in about 15-20 minutes!

**Let's do this!** 🎉

---

*Deployment Guide Version: 1.0*
*Date: October 5, 2025*
*Status: Ready to Deploy ✅*
