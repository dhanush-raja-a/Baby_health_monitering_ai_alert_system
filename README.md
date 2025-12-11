# 👶 Baby Health AI Monitor

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?style=for-the-badge&logo=flask&logoColor=white)
![AI Powered](https://img.shields.io/badge/AI-Groq_API-purple?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **A smart, AI-powered assistant for monitoring your baby's health and getting instant risk assessments.**

---

## 📖 Overview

**Baby Health AI Monitor** is a comprehensive web application designed to help parents track their baby's health vitals. By logging daily health metrics like temperature, symptoms, food intake, and stool status, the system uses **Advanced AI (Groq/Llama)** to analyze the data instantly. It provides an immediate risk assessment (Normal, Monitor Closely, or Seek Medical Attention) and sends email alerts for high-risk situations.

## ✨ Key Features

-   **🔐 Secure User System**: Complete signup and login functionality for parents.
-   **🧸 Multi-Baby Profile**: Manage health logs for multiple babies under a single parent account.
-   **🩺 Detailed Health Logging**: Track Temperature, Cough, Runny Nose, Vomiting, Stool type, and Diet.
-   **🤖 AI Risk Analysis**: Real-time integration with **Groq API** to analyze symptoms and suggest immediate actions.
-   **📧 Instant Email Alerts**: Automatically notifies parents via email if the AI detects a high-risk scenario.
-   **📊 Visual History**: View past health logs with color-coded risk indicators for easy tracking.
-   **🇮🇳 Localized Time**: Displays logs in Indian Standard Time (IST) for convenience.

## 🛠️ Tech Stack

-   **Backend**: Python, Flask, SQLAlchemy (ORM)
-   **Database**: SQLite (Simple & efficient for local use)
-   **AI Engine**: Groq API (Llama-3 models)
-   **Frontend**: HTML5, CSS3, Bootstrap 5 (Responsive Glassmorphism Design)
-   **Utilities**: `pytz` (Timezones), `smtplib` (Email), `python-dotenv` (Config)

## 🚀 Getting Started

Follow these instructions to set up the project on your local machine.

### Prerequisites
-   Python 3.8 or higher installed.
-   A [Groq API Key](https://console.groq.com/) (for AI analysis).
-   A Gmail account (and App Password) for sending email alerts.

### Installation

1.  **Clone the Repository** (or download the source code):
    ```bash
    git clone https://github.com/yourusername/baby-health-monitor.git
    cd baby-health-monitor
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your keys:
    ```ini
    FLASK_SECRET_KEY=your_secret_key_here
    GROQ_API_KEY=your_groq_api_key_here
    EMAIL_USER=your_email@gmail.com
    EMAIL_PASS=your_email_app_password
    ```

5.  **Initialize the Database**:
    ```bash
    flask init-db
    ```

6.  **Run the Application**:
    ```bash
    python app.py
    ```
    Visit `http://127.0.0.1:8000` in your browser.

## 📂 Project Structure

```
├── app.py              # Main Flask application entry point
├── models.py           # Database models (User, BabyProfile, HealthLog)
├── services.py         # AI analysis and Email logic
├── requirements.txt    # Python dependencies
├── .env                # Secret keys (Not committed to repo)
├── instance/           # Contains SQLite database
├── static/             # CSS, Images, JS
└── templates/          # HTML Templates (Jinja2)
    ├── base.html       # Layout template
    ├── login.html      # Authentication pages
    ├── dashboard.html  # Main user dashboard
    ├── enter_log.html  # Health logging form
    └── view_logs.html  # History view
```

## 📸 Usage

1.  **Sign Up**: Create an account.
2.  **Add Baby**: Create a profile for your child (Name, DOB, etc.).
3.  **Enter Log**: Click on your baby's card to add a health log. Enter temperature, symptoms, etc.
4.  **View Advice**: Read the AI's immediate risk assessment and advice.
5.  **Check Email**: If the risk is high ("Seek Medical Attention"), check your inbox for the alert.

## 🔮 Future Enhancements

-   [ ] Vaccination Scheduler & Reminders.
-   [ ] Growth Charts (Weight/Height visualization).
-   [ ] PDF Report Generation for Doctors.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---
*Built with ❤️ for better baby health.*
