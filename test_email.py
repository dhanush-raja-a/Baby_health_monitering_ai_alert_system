import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def test_email():
    print("--- User Config ---")
    user = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')
    print(f"User: {user}")
    print(f"Pass: {'*' * len(password) if password else 'None'}")
    
    if not user or "your_email" in user:
        print("❌ ERROR: Please update .env with your real email.")
        return

    msg = MIMEText("This is a test email from your Baby Health Monitor.")
    msg['Subject'] = "Test Email"
    msg['From'] = user
    msg['To'] = user # Send to self

    print("\n--- Connecting to SMTP ---")
    try:
        # Using Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            print("Login...")
            server.login(user, password)
            print("Sending...")
            server.send_message(msg)
        print("✅ SUCCESS: Email sent! Check your inbox.")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("\nPossible fixes:")
        print("1. Are you using Gmail? You MUST use an 'App Password', not your login password.")
        print("2. Check internet connection.")

if __name__ == "__main__":
    test_email()
