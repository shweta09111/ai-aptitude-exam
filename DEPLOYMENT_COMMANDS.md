# Azure VM Deployment Commands

## ✅ Successfully Connected!
You're now logged into: `azureuser@ai-aptitude-exam`

---

## Step 1: Update System and Install Dependencies

```bash
# Update package list
sudo apt update

# Install Python, pip, git, nginx, and other essentials
sudo apt install -y python3 python3-pip python3-venv git nginx

# Install PostgreSQL (optional, using SQLite for now)
# sudo apt install -y postgresql postgresql-contrib
```

---

## Step 2: Clone Your Repository

```bash
# Navigate to home directory
cd ~

# Clone your GitHub repository
git clone https://github.com/shweta09111/ai-aptitude-exam.git

# Navigate to project directory
cd ai-aptitude-exam/project
```

---

## Step 3: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

---

## Step 4: Set Up Environment Variables

```bash
# Create .env file
nano .env
```

Add these lines to the `.env` file:
```
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///instance/aptitude_exam.db
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## Step 5: Initialize Database

```bash
# Create instance directory if it doesn't exist
mkdir -p instance

# Run database migrations or setup
python3 app.py
# OR if you have a setup script:
# python3 migrate_db.py
```

---

## Step 6: Test the Application

```bash
# Run Flask app to test (press Ctrl+C to stop after testing)
python3 app.py
```

Open another terminal on your local machine and test:
```powershell
curl http://20.40.44.73:5000
```

If it works, press `Ctrl+C` in the SSH session to stop Flask.

---

## Step 7: Set Up Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Test Gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

Press `Ctrl+C` after testing.

---

## Step 8: Create Systemd Service for Auto-Start

```bash
# Create systemd service file
sudo nano /etc/systemd/system/aptitude-exam.service
```

Add this content:
```ini
[Unit]
Description=Aptitude Exam Flask Application
After=network.target

[Service]
User=azureuser
WorkingDirectory=/home/azureuser/ai-aptitude-exam/project
Environment="PATH=/home/azureuser/ai-aptitude-exam/project/venv/bin"
ExecStart=/home/azureuser/ai-aptitude-exam/project/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Save with `Ctrl+X`, `Y`, `Enter`.

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable aptitude-exam

# Start the service
sudo systemctl start aptitude-exam

# Check status
sudo systemctl status aptitude-exam
```

---

## Step 9: Configure Nginx as Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/aptitude-exam
```

Add this content:
```nginx
server {
    listen 80;
    server_name 20.40.44.73;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/azureuser/ai-aptitude-exam/project/static;
        expires 30d;
    }
}
```

Save with `Ctrl+X`, `Y`, `Enter`.

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/aptitude-exam /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx
```

---

## Step 10: Configure Firewall

```bash
# Allow HTTP, HTTPS, and SSH
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check firewall status
sudo ufw status
```

---

## Step 11: Verify Deployment

Open your browser and visit:
- **http://20.40.44.73**

You should see your Aptitude Exam application! 🎉

---

## Useful Commands for Management

### View Application Logs
```bash
# Systemd service logs
sudo journalctl -u aptitude-exam -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart application
sudo systemctl restart aptitude-exam

# Restart Nginx
sudo systemctl restart nginx
```

### Update Application
```bash
cd ~/ai-aptitude-exam/project
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart aptitude-exam
```

### Check Service Status
```bash
sudo systemctl status aptitude-exam
sudo systemctl status nginx
```

---

## 🎉 Deployment Complete!

Your application is now live at: **http://20.40.44.73**

For HTTPS/SSL setup, refer to Let's Encrypt documentation or Azure's SSL certificate services.
