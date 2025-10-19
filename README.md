# 🛡️ AI-Powered Phishing Email Analyzer

Automate phishing email detection and classification using **NLP** with a **Flask-based web interface**.  
This tool helps Security Operations Centers (SOCs) reduce alert fatigue by prioritizing suspicious emails and visualizing phishing campaigns.

---

## 🔍 Overview

- Fetches emails via **IMAP**.  
- Extracts key features: sender, subject, URLs, attachments, and content.  
- Classifies emails as **Benign**, **Suspicious**, or **Phishing** using an NLP-based model.  
- Provides a **web dashboard** with Flask to view classified emails and statistics.  
- Lightweight and easy to deploy — uses **mock threat intelligence** for demonstration.

---

## ⚙️ Features

- 📬 **Email Fetching:** Connects to your email server and fetches new messages.  
- 🤖 **AI Classification:** NLP-based model automatically identifies phishing content.  
- 📊 **Dashboard:** Displays top phishing campaigns, email counts by category, and other statistics.  
- 📝 **Mock IOC Lookup:** Simple internal dictionary to mark known malicious URLs and domains.  
- 💡 **Easy to Extend:** Add custom rules, classifiers, or UI features.

---

## 🚀 Tech Stack

- **Language:** Python 3  
- **Web Framework:** Flask  
- **Machine Learning:** scikit-learn (`RandomForestClassifier`, `TfidfVectorizer`), Pandas, SciPy  
- **Core Libraries:** urlextract, imaplib, re, python-dotenv  
- **Frontend:** HTML, CSS, JavaScript (with Fetch API)  
- **Protocol:** IMAP (for email fetching)  

---

## 💻 Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/phishing-email-analyzer.git
cd phishing-email-analyzer
