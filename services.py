import os
import smtplib
from email.mime.text import MIMEText
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

def analyze_risk(health_data):
    """
    Analyzes health data using Groq API to determine risk level.
    Returns: (Risk Level String, Analysis Text)
    """
    if not GROQ_API_KEY or "your_groq_api_key" in GROQ_API_KEY:
        print("Mocking AI Analysis due to missing key")
        # Mock logic for testing without burning credits or if key invalid
        if health_data['temperature'] > 38.5:
            return "Seek Medical Attention", "High fever detected. Please consult a doctor immediately."
        return "Normal", "Vitals look stable."

    prompt = f"""
    Analyze the following baby health log and determine the risk level.
    
    Data:
    - Age: {health_data['age']}
    - Temperature: {health_data['temperature']} C
    - Symptoms: {health_data['symptoms']}
    - Severity: {health_data['severity']}
    - Duration: {health_data['duration']}
    - Stool: {health_data['stool']}
    
    Output ONLY one of these exact Risk Levels on the first line: "Normal", "Monitor Closely", "Seek Medical Attention".
    On the second line, provide a very brief advice (max 20 words).
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # or mix-7b depending on availability
        )
        response = chat_completion.choices[0].message.content.strip()
        lines = response.split('\n')
        risk_level = lines[0].strip()
        advice = lines[1].strip() if len(lines) > 1 else ""
        
        # Fallback normalization just in case
        if "Seek" in risk_level: risk_level = "Seek Medical Attention"
        elif "Monitor" in risk_level: risk_level = "Monitor Closely"
        else: risk_level = "Normal"
        
        return risk_level, advice
    except Exception as e:
        print(f"AI Error: {e}")
        return "Monitor Closely", "AI Service Unavailable. Please check manually."

def send_alert_email(to_email, baby_name, risk_level, health_data):
    """
    Sends an email alert. 
    """
    sender_email = os.getenv('EMAIL_USER')
    sender_pass = os.getenv('EMAIL_PASS')
    
    if not sender_email or "your_email" in sender_email:
        print(f"Mocking Email to {to_email}: [{risk_level}] for {baby_name}")
        return True

    subject = f"Health Alert: {baby_name} - {risk_level}"
    body = f"""
    Baby Health Alert
    
    Name: {baby_name}
    Risk Level: {risk_level}
    
    Vitals:
    - Temperature: {health_data['temperature']} C
    - Symptoms: {health_data['symptoms']}
    
    Please take appropriate action.
    """
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        # Using Gmail SMTP as an example
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_pass)
            server.send_message(msg)
        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False
