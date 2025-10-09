# 🚀 DEPLOY TO AZURE - COMPLETE GUIDE

## ✅ All Changes Ready to Deploy:

### **Recent Updates:**
1. ✅ User Management System (15 users per page)
2. ✅ Professional UI with gradients and clean design
3. ✅ ML Status page working
4. ✅ Real-time Dashboard icons fixed
5. ✅ Admin Dashboard with 9 action cards
6. ✅ Pagination and sorting working
7. ✅ All templates styled consistently

---

## 🔧 Pre-Deployment Checklist:

### **1. Verify Local System:**
```bash
# Test locally one more time
http://127.0.0.1:5001

# Check these pages work:
- Admin Dashboard: http://127.0.0.1:5001/admin/dashboard ✓
- User Management: http://127.0.0.1:5001/admin/users ✓
- ML Status: http://127.0.0.1:5001/admin/ml_status ✓
- Realtime Dashboard: http://127.0.0.1:5001/realtime_dashboard ✓
```

### **2. Database Status:**
- ✅ 77 users (1 admin, 76 students)
- ✅ User management working
- ✅ Pagination at 15 per page
- ✅ Database file: `aptitude_exam.db`

---

## 📦 Step 1: Commit All Changes

```powershell
# Navigate to project directory
cd F:\ai_aptitude_exam\project

# Check git status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Complete UI overhaul: User management, ML status, pagination, professional design"

# Push to GitHub
git push origin main
```

---

## 🌐 Step 2: Deploy to Azure VM

### **Option A: SSH Deployment (Recommended)**

```bash
# 1. SSH into your Azure VM
ssh azureuser@<your-vm-ip>

# 2. Navigate to application directory
cd /home/azureuser/ai-aptitude-exam

# 3. Stop the service
sudo systemctl stop ai-aptitude-exam

# 4. Backup current database (IMPORTANT!)
cp aptitude_exam.db aptitude_exam.db.backup-$(date +%Y%m%d)

# 5. Pull latest changes
sudo git fetch origin
sudo git reset --hard origin/main

# 6. Install any new dependencies (if needed)
source venv/bin/activate
pip install -r requirements.txt

# 7. Copy database to correct location
sudo cp aptitude_exam.db /home/azureuser/ai-aptitude-exam/

# 8. Set proper permissions
sudo chown azureuser:azureuser /home/azureuser/ai-aptitude-exam/aptitude_exam.db
sudo chmod 644 /home/azureuser/ai-aptitude-exam/aptitude_exam.db

# 9. Restart the service
sudo systemctl restart ai-aptitude-exam

# 10. Check status
sudo systemctl status ai-aptitude-exam

# 11. Check logs for any errors
sudo journalctl -u ai-aptitude-exam -n 50 --no-pager
```

### **Option B: Upload Database via SCP**

```powershell
# From your local machine (if you want to upload your local database)
scp F:\ai_aptitude_exam\project\aptitude_exam.db azureuser@<your-vm-ip>:/home/azureuser/ai-aptitude-exam/

# Then SSH and restart
ssh azureuser@<your-vm-ip>
sudo systemctl restart ai-aptitude-exam
```

---

## 🔍 Step 3: Verify Deployment

### **Check Application:**
```bash
# Open your Azure VM public URL in browser
http://<your-vm-ip>:5001

# Or if you have domain:
http://your-domain.com
```

### **Test Key Features:**

1. **Login Page:**
   - http://your-domain.com/login
   - Try logging in as admin

2. **Admin Dashboard:**
   - http://your-domain.com/admin/dashboard
   - Should show 9 action cards
   - Check statistics load correctly

3. **User Management:**
   - http://your-domain.com/admin/users
   - Should show 15 users per page
   - Test pagination works
   - Verify admin is first in list

4. **ML Status:**
   - http://your-domain.com/admin/ml_status
   - Should show 3 status cards

5. **Realtime Dashboard:**
   - http://your-domain.com/realtime_dashboard
   - All activity icons should display

### **Check Logs:**
```bash
# SSH into VM
ssh azureuser@<your-vm-ip>

# View real-time logs
sudo journalctl -u ai-aptitude-exam -f

# Check for errors
sudo journalctl -u ai-aptitude-exam -n 100 --no-pager | grep -i error
```

---

## 🔧 Step 4: Troubleshooting

### **If Service Won't Start:**
```bash
# Check service status
sudo systemctl status ai-aptitude-exam

# View detailed logs
sudo journalctl -u ai-aptitude-exam -n 100 --no-pager

# Check if port is in use
sudo netstat -tulpn | grep 5001

# Manually test Python
cd /home/azureuser/ai-aptitude-exam
source venv/bin/activate
python app.py
```

### **If Database Issues:**
```bash
# Check database exists
ls -lh /home/azureuser/ai-aptitude-exam/aptitude_exam.db

# Check permissions
sudo chown azureuser:azureuser /home/azureuser/ai-aptitude-exam/aptitude_exam.db
sudo chmod 644 /home/azureuser/ai-aptitude-exam/aptitude_exam.db

# Test database
sqlite3 /home/azureuser/ai-aptitude-exam/aptitude_exam.db "SELECT COUNT(*) FROM users;"
```

### **If CSS Not Loading:**
```bash
# Clear Flask cache
rm -rf /home/azureuser/ai-aptitude-exam/__pycache__
rm -rf /home/azureuser/ai-aptitude-exam/templates/__pycache__

# Restart service
sudo systemctl restart ai-aptitude-exam
```

---

## 📋 Quick Deploy Commands (All-in-One)

### **From Local Machine:**
```powershell
# 1. Commit and push
cd F:\ai_aptitude_exam\project
git add .
git commit -m "Deploy: User management, ML status, UI improvements"
git push origin main
```

### **On Azure VM:**
```bash
# 2. SSH and deploy
ssh azureuser@<your-vm-ip>

# 3. Run deployment script
cd /home/azureuser/ai-aptitude-exam
sudo systemctl stop ai-aptitude-exam
sudo git fetch origin
sudo git reset --hard origin/main
sudo systemctl restart ai-aptitude-exam
sudo systemctl status ai-aptitude-exam
```

---

## 🎯 Post-Deployment Checklist:

- [ ] Login page loads
- [ ] Admin can log in
- [ ] Admin dashboard shows 9 cards
- [ ] User management displays 15 users per page
- [ ] Pagination works
- [ ] Edit user works
- [ ] Delete user works
- [ ] Add user works
- [ ] ML Status page displays
- [ ] Realtime Dashboard shows icons
- [ ] All CSS and styling loads correctly
- [ ] No console errors in browser
- [ ] Database queries work
- [ ] Service runs without errors

---

## 🔐 Important Notes:

### **Database:**
- ✅ Your local database has 77 users (1 admin, 76 students)
- ✅ Make sure to backup before deploying
- ✅ If Azure has different users, decide which database to keep

### **Environment:**
- ✅ Azure should use production mode
- ✅ Debug should be False in production
- ✅ Check `config.py` settings

### **Security:**
- ✅ Admin password is working
- ✅ All routes have proper authentication
- ✅ Session management working

---

## 📞 Need Help?

If deployment fails, check:

1. **Git Repository:**
   ```bash
   # Check if push succeeded
   git remote -v
   git log --oneline -5
   ```

2. **Azure VM Status:**
   ```bash
   # Check VM is running
   # Check firewall allows port 5001
   # Check service is enabled
   sudo systemctl is-enabled ai-aptitude-exam
   ```

3. **Application Logs:**
   ```bash
   # Detailed error logs
   sudo journalctl -u ai-aptitude-exam --since "10 minutes ago"
   ```

---

## 🎉 After Successful Deployment:

Your application will be live with:
- ✨ Professional gradient UI
- 👥 User management (15 per page)
- 🧠 ML Status monitoring
- 📊 Real-time dashboard with icons
- 🎨 Consistent styling across all pages
- 🔐 Secure admin access

**Your live URL:** `http://<your-azure-vm-ip>:5001`

Good luck with your deployment! 🚀
