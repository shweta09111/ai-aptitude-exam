# 🎓 STUDENT DEPLOYMENT GUIDE - FREE FOR YEARS!

## ✅ Your Project: AI Aptitude Exam System
- 6.6 GB with full ML features
- PyTorch + Transformers + BERT
- 1,013 questions + Analytics
- **Deploy 100% FREE as a student!**

---

## 🚀 PHASE 1: AZURE FOR STUDENTS (START NOW - 10 minutes)

### **STEP 1: Sign Up for Azure for Students**

1. **Go to:** https://azure.microsoft.com/en-us/free/students/
2. **Click:** "Activate now" or "Start free"
3. **Sign in** with Microsoft account (or create one)
4. **Verify student status:**
   - Use your school email (.edu or .ac.in)
   - OR upload student ID
5. **Get instant approval** (usually within minutes!)
6. **Receive $100 credit** - no credit card needed!

### **STEP 2: Create Virtual Machine**

Once approved:

1. **Login to:** https://portal.azure.com
2. **Click:** "Create a resource"
3. **Select:** "Virtual Machine"
4. **Configure:**

```
Basics:
- Resource group: Create new → "ai-exam-rg"
- VM name: "ai-aptitude-exam"
- Region: (Closest to you - e.g., "East US" or "Southeast Asia")
- Image: "Ubuntu Server 22.04 LTS"
- Size: "Standard_B2s" (2 vCPUs, 4GB RAM) ✅ FREE eligible
  OR "Standard_B4ms" (4 vCPUs, 16GB RAM) for better performance

Authentication:
- Type: SSH public key
- Username: azureuser
- SSH key: Generate new key pair
- Download the key file (SAVE IT!)

Inbound ports:
- Select: SSH (22), HTTP (80), HTTPS (443)
```

5. **Click:** "Review + create"
6. **Click:** "Create"
7. **Download SSH key** when prompted (important!)
8. **Wait 2-3 minutes** for VM to deploy

### **STEP 3: Get Your VM IP Address**

1. Go to **"Virtual machines"**
2. Click on **"ai-aptitude-exam"**
3. Copy the **"Public IP address"** (e.g., 20.123.45.67)

---

## 🔧 PHASE 2: SETUP YOUR SERVER (20 minutes)

### **STEP 1: Connect to Your VM**

**On Windows (PowerShell):**

```powershell
# Navigate to where you saved the SSH key
cd ~\Downloads

# Fix permissions on key file
icacls "ai-aptitude-exam_key.pem" /inheritance:r
icacls "ai-aptitude-exam_key.pem" /grant:r "$($env:USERNAME):(R)"

# Connect to VM
ssh -i ai-aptitude-exam_key.pem azureuser@YOUR_VM_IP
```

Replace `YOUR_VM_IP` with your actual IP address!

**First time:** Type `yes` when asked about authenticity

### **STEP 2: Update System**

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y build-essential python3-pip python3-dev git nginx postgresql postgresql-contrib
```

### **STEP 3: Install Python 3.11**

```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Set as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### **STEP 4: Clone Your Repository**

```bash
# Clone your GitHub repo
git clone https://github.com/shweta09111/ai-aptitude-exam.git
cd ai-aptitude-exam

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### **STEP 5: Install Dependencies**

```bash
# Install requirements (this takes 10-15 minutes due to PyTorch)
pip install -r requirements_local.txt

# If you get memory errors, install in parts:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers
pip install -r requirements.txt
```

### **STEP 6: Setup PostgreSQL Database**

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE aptitude_exam;
CREATE USER examuser WITH PASSWORD 'your_secure_password_123';
ALTER ROLE examuser SET client_encoding TO 'utf8';
ALTER ROLE examuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE examuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE aptitude_exam TO examuser;
\q
```

### **STEP 7: Configure Environment Variables**

```bash
# Create .env file
nano .env

# Add these (press Ctrl+X, Y, Enter to save):
```

```env
DATABASE_URL=postgresql://examuser:your_secure_password_123@localhost/aptitude_exam
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production
```

### **STEP 8: Initialize Database**

```bash
# Make sure you're in the project directory and venv is activated
cd ~/ai-aptitude-exam
source venv/bin/activate

# Run database initialization
python3 -c "from app import app; app.app_context().push(); from app import init_db; init_db()"

# Or if you have init route:
python3 -c "import requests; print(requests.get('http://localhost:5000/init_db').text)"
```

### **STEP 9: Test Your App Locally**

```bash
# Run the app
python3 app.py

# Should see:
# * Running on http://0.0.0.0:5000
```

Open another terminal and test:
```bash
curl http://localhost:5000
```

If you see HTML, it's working! Press Ctrl+C to stop.

---

## 🌐 PHASE 3: DEPLOY WITH NGINX (10 minutes)

### **STEP 1: Create Gunicorn Service**

```bash
# Create systemd service file
sudo nano /etc/systemd/system/aiexam.service
```

Add this content:

```ini
[Unit]
Description=AI Aptitude Exam Gunicorn Service
After=network.target

[Service]
User=azureuser
Group=www-data
WorkingDirectory=/home/azureuser/ai-aptitude-exam
Environment="PATH=/home/azureuser/ai-aptitude-exam/venv/bin"
ExecStart=/home/azureuser/ai-aptitude-exam/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app --timeout 120

[Install]
WantedBy=multi-user.target
```

Save (Ctrl+X, Y, Enter)

### **STEP 2: Start Gunicorn Service**

```bash
# Start and enable service
sudo systemctl start aiexam
sudo systemctl enable aiexam

# Check status
sudo systemctl status aiexam
```

Should see "active (running)" ✅

### **STEP 3: Configure Nginx**

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/aiexam
```

Add this:

```nginx
server {
    listen 80;
    server_name YOUR_VM_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /static {
        alias /home/azureuser/ai-aptitude-exam/static;
    }
}
```

Replace `YOUR_VM_IP` with your actual IP!

### **STEP 4: Enable Nginx Config**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/aiexam /etc/nginx/sites-enabled/

# Remove default config
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## 🎉 PHASE 4: YOUR APP IS LIVE!

### **Access Your App:**

Open browser: `http://YOUR_VM_IP`

You should see your AI Aptitude Exam System! 🎉

---

## 📊 AZURE CREDIT TRACKING

**Your $100 credit:**
- Standard_B2s (2 vCPU, 4GB): ~$30/month = **3+ months FREE**
- Standard_B4ms (4 vCPU, 16GB): ~$60/month = **1.5+ months FREE**

**Check remaining credit:**
1. Go to: https://www.microsoftazuresponsorships.com/
2. View your balance

**Renews yearly while you're a student!** 🎓

---

## 🔧 MAINTENANCE COMMANDS

### **View Logs:**
```bash
# Application logs
sudo journalctl -u aiexam -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### **Restart Services:**
```bash
# Restart app
sudo systemctl restart aiexam

# Restart Nginx
sudo systemctl restart nginx
```

### **Update Code:**
```bash
cd ~/ai-aptitude-exam
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart aiexam
```

---

## 🎯 PHASE 5: GITHUB STUDENT PACK (APPLY NOW)

While Azure is running, apply for GitHub Pack:

### **STEP 1: Apply**

1. Go to: https://education.github.com/pack
2. Click "Get student benefits"
3. Sign in with GitHub
4. Add school email
5. Upload student ID or enrollment proof
6. Submit application

### **STEP 2: Wait for Approval** (1-3 days)

You'll get email when approved!

### **STEP 3: Claim DigitalOcean Credit**

Once approved:
1. Go to GitHub Student Pack dashboard
2. Find "DigitalOcean"
3. Click "Get access"
4. Create DigitalOcean account
5. Apply $200 credit
6. Use for 4 more months!

---

## 💡 YOUR FREE DEPLOYMENT TIMELINE

```
Month 1-2:   Azure $100 credit ✅
Month 3-4:   GitHub Pack DigitalOcean $200 ✅
Month 5-12:  Azure renewed (yearly) ✅
Month 12+:   Switch to Oracle Cloud Always Free ✅

TOTAL: FREE for entire degree! 🎓
```

---

## 🚨 TROUBLESHOOTING

### **Issue: Can't connect via SSH**
```bash
# Check Azure firewall rules allow SSH (port 22)
# Verify you're using correct IP and key file
```

### **Issue: App not loading**
```bash
# Check app is running
sudo systemctl status aiexam

# Check Nginx is running
sudo systemctl status nginx

# Check ports
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :80
```

### **Issue: Database connection error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U examuser -d aptitude_exam -h localhost
```

### **Issue: Out of memory**
```bash
# Create swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📞 NEED HELP?

**Azure Support:** Free for students!
- Portal: https://portal.azure.com
- Student forum: https://learn.microsoft.com/answers/

**Your Project:** Already on GitHub
- Repository: https://github.com/shweta09111/ai-aptitude-exam

---

## ✅ CHECKLIST

- [ ] Azure for Students account created
- [ ] $100 credit activated
- [ ] VM created and running
- [ ] SSH connection working
- [ ] Python 3.11 installed
- [ ] Code cloned from GitHub
- [ ] Dependencies installed
- [ ] PostgreSQL configured
- [ ] App tested locally
- [ ] Gunicorn service running
- [ ] Nginx configured
- [ ] **APP IS LIVE!** 🎉
- [ ] GitHub Student Pack application submitted
- [ ] Waiting for GitHub approval (1-3 days)

---

**🎓 STUDENT POWER: Deploy professionally for FREE!** 🚀

Your AI Aptitude Exam System with ALL features is now live!
