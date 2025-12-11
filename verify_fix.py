import requests
import time

# Login to get session
session = requests.Session()
# Assuming default devbox secret key allows client side session manipulation or we just use the login form
# For simplicity, let's use the login endpoint if possible, but we don't know the user credentials from here easily without looking at DB.
# Let's mock the test within the app context using Flask's test client which is easier.

from app import app, db, User, BabyProfile

def test_deduplication():
    # Setup
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # Get a user and baby
        user = User.query.first()
        if not user:
            print("No user found to test with.")
            return
            
        baby = BabyProfile.query.filter_by(user_id=user.id).first()
        if not baby:
            print("No baby found to test with.")
            return

        print(f"Testing with User: {user.email}, Baby: {baby.name} (ID: {baby.id})")

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user.id

            # Data for log
            data = {
                'temperature': 37.5,
                'symptom_severity': 'Mild',
                'symptom_duration': '1 day',
                'stool_status': 'Normal'
            }

            # First Request
            print("Sending First Request...")
            response1 = client.post(f'/enter_log/{baby.id}', data=data, follow_redirects=True)
            print(f"First Request Status: {response1.status_code}")
            
            # Second Request immediately
            print("Sending Second Request (Duplicate)...")
            response2 = client.post(f'/enter_log/{baby.id}', data=data, follow_redirects=True)
            print(f"Second Request Status: {response2.status_code}")
            
            # Check response content for flash message
            if b"Log already saved recently" in response2.data:
                print("SUCCESS: Duplicate prevented and flash message found.")
            else:
                print("FAILURE: Duplicate NOT prevented or flash message missing.")
                # print(response2.data)

if __name__ == "__main__":
    test_deduplication()
