from app import app, db, User, BabyProfile

def test_routes():
    # Setup
    app.config['TESTING'] = True
    
    with app.app_context():
        # Get a user and login
        user = User.query.first()
        if not user:
            print("No user found to test with.")
            return
            
        # Get a baby for the edit route
        baby = BabyProfile.query.filter_by(user_id=user.id).first()
        if not baby:
             print("No baby found to test edit route.")
             return

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user.id

            # Define routes to test
            routes = [
                '/analytics',
                '/wheezing',
                '/profile',
                '/select_log_baby',
                '/dashboard',
                f'/edit_baby/{baby.id}'
            ]
            
            print(f"Testing routes for user: {user.email}")
            
            for route in routes:
                response = client.get(route, follow_redirects=True)
                if response.status_code == 200:
                   print(f"SUCCESS: {route} loaded (200 OK)")
                else:
                    print(f"FAILURE: {route} failed with {response.status_code}")

if __name__ == "__main__":
    test_routes()
