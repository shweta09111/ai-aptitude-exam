# 🎓 AI-Augmented Online Aptitude Exam System

> An intelligent, adaptive online examination platform powered by AI for automated question generation, difficulty classification, and real-time proctoring.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

The **AI-Augmented Online Aptitude Exam System** revolutionizes traditional online assessments by integrating cutting-edge artificial intelligence to create a secure, adaptive, and intelligent testing environment. This platform is designed for educational institutions, corporate recruiters, and certification bodies who need scalable, fair, and sophisticated assessment solutions.

### Why This Project?

Traditional online exam platforms face several critical challenges:
- **Manual Content Creation**: Question authoring is time-consuming and expensive
- **Static Difficulty**: Fixed question sets don't adapt to individual skill levels
- **Security Concerns**: Cheating and academic dishonesty are difficult to prevent
- **Limited Analytics**: Lack of insights into candidate performance patterns
- **Scalability Issues**: Difficulty handling large concurrent user loads

Our platform addresses these challenges through:
- Automated AI-powered question generation using state-of-the-art language models
- Adaptive testing that adjusts difficulty based on real-time performance
- Computer vision-based proctoring for exam integrity
- Cloud synchronization for distributed exam management
- Comprehensive analytics and reporting

---

## ✨ Key Features

### 🤖 Intelligent Question Generation
- **T5 Transformer Model**: Generates contextually relevant multiple-choice questions
- **Answer Extraction**: Automated QA pipeline creates accurate answers with confidence scores
- **Duplicate Detection**: Smart algorithms prevent repetitive content
- **Topic-Based Generation**: Create questions on demand for specific subjects

### 🎯 Adaptive Testing Engine
- **Real-Time Adaptation**: Adjusts question difficulty based on user performance
- **Performance Analytics**: Tracks response patterns and learning curves
- **Personalized Exams**: Tailors assessment flow to individual proficiency levels

### 🔍 BERT-Powered Classification
- **Difficulty Analysis**: Automatically classifies questions as easy, medium, or hard
- **Topic Categorization**: Organizes questions by subject and category
- **Semantic Understanding**: Uses deep learning for accurate classification

### 📹 Real-Time Proctoring
- **Face Detection**: OpenCV-based monitoring ensures candidate presence
- **Eye Tracking**: Detects gaze patterns to identify suspicious behavior
- **Session Logging**: Records proctoring events for post-exam review
- **Anomaly Detection**: Flags unusual activities during exams

### ☁️ Cloud Synchronization
- **Supabase Integration**: Seamless cloud database synchronization
- **Distributed Management**: Support for multi-location exam deployment
- **Automatic Backup**: Questions and results synced to the cloud
- **Offline Mode**: Continue exams during temporary connectivity loss

### ⚙️ Background Automation
- **Scheduled Scraping**: Periodically fetches questions from educational websites
- **Automated Classification**: Continuously classifies new questions
- **Periodic Generation**: Generates fresh content at configured intervals
- **Cloud Sync Jobs**: Automated upload/download synchronization

### 📊 Comprehensive Analytics
- **Performance Dashboards**: Visual insights into exam statistics
- **User Analytics**: Track individual and group performance trends
- **Question Analytics**: Identify difficult questions and improve content
- **Export Reports**: Generate CSV/PDF reports for stakeholders

---

## 🛠 Technology Stack

### Backend
- **Python 3.11+**: Core programming language
- **Flask**: Lightweight web framework
- **SQLite**: Local database (development)
- **PostgreSQL**: Production database (optional)
- **APScheduler**: Background job scheduling

### AI/ML Models
- **Transformers (Hugging Face)**
  - T5 (valhalla/t5-base-qg-hl): Question generation
  - BERT (bert-base-uncased): Text classification
  - DistilBERT: Answer extraction
- **PyTorch**: Deep learning framework
- **Scikit-learn**: Machine learning utilities

### Frontend
- **HTML5/CSS3**: Modern, responsive UI
- **JavaScript (Vanilla)**: Dynamic interactions
- **Jinja2**: Template engine
- **Bootstrap**: UI components

### Computer Vision
- **OpenCV**: Face and eye detection
- **Haar Cascades**: Pre-trained detection models

### Cloud & DevOps
- **Supabase**: Cloud database and authentication
- **Docker**: Containerization
- **Railway/Vercel**: Deployment platforms
- **Git**: Version control

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  (Admin Dashboard, Exam Interface, Analytics, Reports)       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Flask Application Layer                    │
│  • Authentication    • Session Management   • API Endpoints  │
│  • Routing          • Template Rendering   • WebSocket       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Business Logic Layer                       │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Question  │  │   BERT     │  │  Adaptive  │            │
│  │ Generator  │  │ Classifier │  │   Engine   │            │
│  │   (T5)     │  │            │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │    AI      │  │   Cloud    │  │ Background │            │
│  │ Proctoring │  │    Sync    │  │    Jobs    │            │
│  │  (OpenCV)  │  │ (Supabase) │  │(APScheduler)│            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Data Storage Layer                        │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   SQLite (Local) │         │  Supabase Cloud  │          │
│  │  • Questions     │  ◄────► │  • Questions     │          │
│  │  • Users         │         │  • Backup Data   │          │
│  │  • Results       │         │  • Sync Status   │          │
│  │  • Proctoring    │         │                  │          │
│  └──────────────────┘         └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📥 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- 4GB+ RAM (for ML models)
- 2GB+ free disk space

### Step 1: Clone the Repository

```bash
git clone https://github.com/shweta09111/ai-aptitude-exam.git
cd ai-aptitude-exam/project
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements_local.txt
```

### Step 4: Initialize Database

```bash
python app.py
# The database will be automatically created on first run
```

### Step 5: Create Admin Account

```bash
python manage_users.py
# Follow the prompts to create an admin user
```

### Step 6: Run the Application

```bash
python app.py
```

Visit `http://localhost:5001` in your browser.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///instance/aptitude_exam.db

# Supabase Configuration (Optional - for cloud sync)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# ML Model Configuration
USE_GPU=false
MODEL_CACHE_DIR=./trained_models

# Proctoring Configuration
ENABLE_PROCTORING=true
PROCTORING_THRESHOLD=0.7
```

### Application Settings

Edit configuration in `app.py`:

```python
# Background job schedules
SCRAPING_INTERVAL = 60  # minutes
CLASSIFICATION_INTERVAL = 30  # minutes
GENERATION_SCHEDULE = "0 */6 * * *"  # cron format
CLOUD_SYNC_INTERVAL = 12  # hours
```

---

## 🚀 Usage

### For Administrators

1. **Login**: Navigate to `/login/admin` with your credentials
2. **Dashboard**: View system statistics and recent activity
3. **Manage Questions**:
   - Upload CSV files with questions
   - Generate questions using AI
   - Edit/delete existing questions
   - Classify questions by difficulty
4. **Manage Users**:
   - Create student accounts
   - View user performance
   - Reset passwords
5. **Analytics**:
   - View performance reports
   - Export data to CSV
   - Monitor exam sessions
6. **Background Jobs**:
   - Trigger manual scraping
   - Run classification jobs
   - Monitor job status
7. **Cloud Sync**:
   - Upload questions to Supabase
   - Download from cloud
   - View sync status

### For Students

1. **Login**: Navigate to `/login` with your credentials
2. **Dashboard**: View available exams and past results
3. **Take Exam**:
   - Start a new exam session
   - Proctoring will activate (if enabled)
   - Answer questions with adaptive difficulty
   - Submit for instant results
4. **View Results**: Check scores and performance analytics

### API Endpoints

#### Question Generation
```bash
POST /api/generate_questions
Content-Type: application/json

{
  "context": "Python is a high-level programming language...",
  "max_questions": 5
}
```

#### Classification
```bash
POST /api/classify_question
Content-Type: application/json

{
  "question_text": "What is the output of print(2**3)?",
  "options": ["6", "8", "9", "None"]
}
```

#### Cloud Sync
```bash
POST /api/cloud_sync/upload
GET /api/cloud_sync/status
POST /api/cloud_sync/download
```

---

## 📦 Deployment

### Docker Deployment

```bash
# Build image
docker build -t ai-aptitude-exam .

# Run container
docker run -p 5001:5001 -v $(pwd)/instance:/app/instance ai-aptitude-exam
```

### Railway Deployment

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add environment variables
4. Deploy automatically on push

### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

**Note**: Vercel deployment requires PostgreSQL database. Update `DATABASE_URL` in environment variables.

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write docstrings for functions
- Add unit tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Hugging Face**: For providing state-of-the-art NLP models
- **OpenCV**: For computer vision capabilities
- **Supabase**: For cloud database infrastructure
- **IndiaBix, GeeksforGeeks, Javatpoint**: For educational content sources

---

## 📞 Contact & Support

- **Developer**: Shweta
- **Repository**: [github.com/shweta09111/ai-aptitude-exam](https://github.com/shweta09111/ai-aptitude-exam)
- **Issues**: [GitHub Issues](https://github.com/shweta09111/ai-aptitude-exam/issues)

---

## 📊 Project Statistics

- **Total Questions**: 1000+ (and growing with AI generation)
- **Supported Question Types**: MCQ, Adaptive MCQ
- **Active Users**: Scalable to thousands
- **Uptime**: 99.9% (with proper deployment)
- **Response Time**: < 2 seconds (average)

---

## 🔮 Future Roadmap

- [ ] Support for subjective questions with NLP evaluation
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced analytics with ML insights
- [ ] Integration with LMS platforms (Moodle, Canvas)
- [ ] Blockchain-based certificate issuance
- [ ] Voice-based proctoring
- [ ] Gamification features

---

**Made with ❤️ for better education and assessment**
