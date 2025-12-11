from datetime import datetime
import pytz

def ist_time_filter(dt):
    if dt is None:
        return ""
    utc_tz = pytz.timezone('UTC')
    ist_tz = pytz.timezone('Asia/Kolkata')
    # Simulate the filter logic: localize then convert
    # If dt is naive, assume UTC as per DB storagte convention
    if dt.tzinfo is None:
        dt = utc_tz.localize(dt)
    
    ist_dt = dt.astimezone(ist_tz)
    return ist_dt.strftime('%Y-%m-%d %I:%M %p')

def test_timezone():
    # Test case: UTC noon is IST 5:30 PM
    utc_time = datetime(2025, 12, 11, 12, 0, 0) # 12:00 PM UTC
    ist_str = ist_time_filter(utc_time)
    print(f"UTC: {utc_time}")
    print(f"IST Transformed: {ist_str}")
    
    expected = "2025-12-11 05:30 PM"
    if ist_str == expected:
        print("SUCCESS: Time conversion matched expected output.")
    else:
        print(f"FAILURE: Expected {expected}, got {ist_str}")

if __name__ == "__main__":
    test_timezone()
