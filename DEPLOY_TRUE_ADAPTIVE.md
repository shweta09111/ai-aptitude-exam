# Deploy TRUE Adaptive Testing to Azure

## 🚀 Quick Deployment Commands

Run these in your SSH terminal (connected to Azure VM):

### Step 1: Pull the latest changes
```bash
cd ~/ai-aptitude-exam
git pull origin main
```

### Step 2: Restart the application
```bash
sudo systemctl restart ai-aptitude-exam
```

### Step 3: Check the status
```bash
sudo systemctl status ai-aptitude-exam
```

### Step 4: Monitor logs (optional)
```bash
sudo journalctl -u ai-aptitude-exam -f
```

---

## ✅ What Changed

### Before (Random):
- Questions selected randomly
- No difficulty adaptation
- No ability tracking
- ❌ Did NOT match flowchart

### After (TRUE Adaptive):
- ✅ Starts with MEDIUM questions
- ✅ Correct answer → Next HARD question
- ✅ Wrong answer → Next EASY question
- ✅ Tracks student ability using IRT
- ✅ Matches your flowchart exactly!

---

## 🎯 Testing the Adaptive Engine

After deploying, test it:

1. Visit: http://20.40.44.73
2. Login as a student
3. Start Adaptive Exam
4. Answer first question (should be Medium difficulty)
5. If correct → next should be Hard
6. If wrong → next should be Easy

---

## 📊 How It Works Now

```
Start Exam
    ↓
Medium Question (default start)
    ↓
Answer Correct?
    ├─ YES → Ability ↑ → Next Hard Question
    └─ NO → Ability ↓ → Next Easy Question
    ↓
Store Response in adaptive_responses table
    ↓
Update Student Ability (IRT calculation)
    ↓
Select Next Question based on ability
    ↓
Repeat (10 questions total)
    ↓
End Exam with final ability score
```

---

## 🔍 Verify It's Working

Check the logs after taking an exam:
```bash
sudo journalctl -u ai-aptitude-exam | grep "Adaptive question selected"
```

You should see logs like:
```
Adaptive question selected: ID=123, Difficulty=Medium, Ability=0.00
Response recorded: User=1, Q=123, Correct=True, Ability=0.45
Adaptive question selected: ID=456, Difficulty=Hard, Ability=0.45
```

---

## 🎉 Done!

Your adaptive testing now uses TRUE IRT-based adaptation that matches your flowchart!
