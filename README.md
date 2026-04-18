# 🚀 AI Resume Analyzer (ATS with NLP + LLM)

An intelligent **Applicant Tracking System (ATS)** that automates resume screening using **Natural Language Processing (NLP)** and **Large Language Models (LLMs)**.

This system fetches candidate data from **Google Forms/Sheets**, evaluates resumes using **semantic matching**, and provides **AI-powered insights** for recruiters.

---

## 🎯 Features

- 📄 Resume Parsing (PDF)
- 🧠 Skill Extraction (NLP)
- 📊 Hybrid Scoring System
  - Skill Matching
  - Semantic Similarity (Sentence Transformers)
- 🤖 LLM Integration (via OpenRouter)
  - Resume Summarization
  - Candidate Explanation
  - AI Chatbot (Ask anything about candidate)
- 🔗 Google Sheets Integration
- 📈 Dashboard with ranked candidates
- ⚡ Fast processing using caching (`resume_text`)

---

## 🏗️ System Architecture

```
Google Form → Google Sheets → Flask Backend
↓
Resume Parsing (NLP)
↓
Scoring + Semantic Matching
↓
Database (SQLite)
↓
Dashboard + AI Insights
```


---

## 🛠️ Tech Stack

- **Backend**: Flask
- **Database**: SQLite (SQLAlchemy)
- **NLP**:
  - Sentence Transformers (`all-MiniLM-L6-v2`)
  - Skill extraction (custom)
- **LLM**: OpenRouter API (Mistral / GPT / LLaMA)
- **Frontend**: HTML + Tailwind CSS
- **Google APIs**:
  - Google Sheets API
  - Google Drive API (Resume links)
  - OAuth 2.0 Authentication

---

## ⚙️ Installation & Setup

### 1. Clone Repo
```bash
git clone https://github.com/Madhu-Wala/AI-RESUME-ANALYZER.git
cd AI-RESUME-ANALYZER
```

### 2. Create Virtual Environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
```
   
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create .env file:
```bash
OPENROUTER_API_KEY=your_api_key_here
```
---
## 🔑 API Setup Guide

🔹 OpenRouter (LLM API)
1. Go to: https://openrouter.ai/
2. Sign up / Login
3. Generate API Key
4. Add in .env

---
🔹 Google OAuth Setup
1. Go to: https://console.cloud.google.com/
2. Create new project
3. Enable APIs:
  - Google Drive API
  - Google Sheets API
4. Create OAuth Credentials
5. Download client_secret.json
6. Place in root folder

▶️ Running the Project
```bash
python app.py
```

Open browser:
```
http://127.0.0.1:5000
```

## 📌 Usage Flow

**Important:** Make sure you have created your google form for collecting applicant data using the account you are using to signup/login.

1. Login using Google 
2. Enter:
- Job Title
- Google Sheet Link of the Responses of Google form
- Job Description (In text format)
- Column Names (Name, Email, Phone, Resume).

  **Important:** Make sure the column names you enter here are same as in your responses google sheet and there are no leading and trailing spaces in your sheet column names.
3. System will:
- Fetch data from sheet
- Parse resumes
- Score candidates
4. View dashboard:
- Ranked candidates
5. Click candidate:
- View resume
- Generate AI insights
- Ask questions related to candidate hiring.

---

## 🧠 NLP Pipeline

- Resume Text Extraction
- Skill Extraction
- Semantic Embedding
- Cosine Similarity with JD
- Final Score:
```Score = 0.4 * Skill Match + 0.6 * Semantic Similarity```

---

## 🤖 LLM Features

- Resume Summarization
- Candidate Fit Explanation
- Interactive Chatbot

Example Prompt:
```
Explain why should I hire this candidate.
```

---

### 📊 Evaluation Metrics
- Accuracy (Skill Match)
- Semantic Relevance
- LLM Response Quality
- System Performance (Latency)

---

## 🚀 Future Scope
- 🔍 RAG-based resume search (vector DB)
- 📧 Auto email to shortlisted candidates
- 📊 Recruiter analytics dashboard
- 🌍 Multilingual resume analysis
- 🧠 Fine-tuned domain-specific models
- 📁 Cloud deployment (AWS / GCP)

---

## ⚠️ Disclaimer

- This project is for educational purposes only
- AI-generated insights may not always be accurate
- Do not use as the sole decision-making system in real hiring

---

## 📜 License & Rights

- Free to use for academic and personal projects
- Attribution appreciated
- Not intended for commercial deployment without modifications

---

## 👨‍💻 Author

Developed as part of an academic mini-project on:
NLP + LLM Applications

By Madhura Walawalkar

---

## ❤️ Acknowledgements
- OpenRouter API
- Sentence Transformers
- Google APIs
- Flask Community
