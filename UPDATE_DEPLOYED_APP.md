# Update Deployed Application on Azure VM

## Quick Update Commands

Run these commands in your SSH terminal (where you're connected as `azureuser@ai-aptitude-exam`):

### Step 1: Navigate to project directory
```bash
cd ~/ai-aptitude-exam/project
```

### Step 2: Pull latest changes from GitHub
```bash
git pull origin main
```

### Step 3: Activate virtual environment (if not already active)
```bash
source venv/bin/activate
```

### Step 4: Install any new dependencies (if requirements.txt changed)
```bash
pip install -r requirements.txt
```

### Step 5: Restart the application service
```bash
sudo systemctl restart aptitude-exam
```

### Step 6: Check service status
```bash
sudo systemctl status aptitude-exam
```

### Step 7: Restart Nginx (if needed)
```bash
sudo systemctl restart nginx
```

### Step 8: Check logs for any errors
```bash
sudo journalctl -u aptitude-exam -n 50 --no-pager
```

---

## 🎯 All-in-One Update Command

For quick updates, you can run all steps at once:

```bash
cd ~/ai-aptitude-exam/project && \
git pull origin main && \
source venv/bin/activate && \
pip install -r requirements.txt && \
sudo systemctl restart aptitude-exam && \
sudo systemctl status aptitude-exam
```

---

## Verify the Update

After restarting, visit **http://20.40.44.73** in your browser to see the updated:
- ✅ Admin Dashboard (reverted look)
- ✅ Manage Users card
- ✅ Statistical Analytics card
- ✅ ML Status card
- ✅ Updated user management pages (unified styling)
- ✅ Fixed pagination (15 items per page)
- ✅ Fixed realtime dashboard icons

---

## Troubleshooting

### If you see errors:
```bash
# View detailed logs
sudo journalctl -u aptitude-exam -f

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### If static files don't update:
```bash
# Clear browser cache or do a hard refresh (Ctrl+F5)
# Restart Nginx
sudo systemctl restart nginx
```

### If database changes were made:
```bash
# Run migrations if needed
cd ~/ai-aptitude-exam/project
source venv/bin/activate
python3 migrate_db.py
sudo systemctl restart aptitude-exam
```

---

## 🎉 Done!

Your deployed application is now updated with all the latest changes!
