"""
Test script to send a drought alert email via SendGrid
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from services.email_service import send_drought_alert
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test data
TEST_EMAIL = "regan@axiomintelligence.co.nz"
TEST_USER_NAME = "Regan"
TEST_TRIGGER_NAME = "Taranaki Drought Alert - TEST"
TEST_REGION = "Taranaki"
TEST_TRIGGER_ID = 999  # Dummy ID for testing
TEST_USER_ID = 1

# Sample conditions that triggered the alert
TEST_CONDITIONS_MET = [
    {
        "indicator": "temp",
        "operator": ">",
        "threshold_value": 25.0,
        "actual_value": 28.5,
        "met": True
    },
    {
        "indicator": "rainfall",
        "operator": "<",
        "threshold_value": 2.0,
        "actual_value": 0.8,
        "met": True
    },
    {
        "indicator": "humidity",
        "operator": "<",
        "threshold_value": 60.0,
        "actual_value": 45.0,
        "met": True
    }
]

# Sample recommendations
TEST_RECOMMENDATIONS = [
    {
        "title": "High Temperature Alert",
        "description": "Temperature is critically high (28.5°C). Consider implementing irrigation schedules and providing shade for livestock."
    },
    {
        "title": "Low Rainfall",
        "description": "Rainfall is below threshold (0.8mm). Monitor soil moisture levels and prepare for extended dry period."
    },
    {
        "title": "Low Humidity",
        "description": "Humidity levels are low (45%). Increased evaporation expected - adjust water management accordingly."
    }
]

print("=" * 80)
print("CKCIAS DROUGHT MONITOR - EMAIL SERVICE TEST")
print("=" * 80)
print()
print(f"Sending test drought alert email to: {TEST_EMAIL}")
print(f"Trigger: {TEST_TRIGGER_NAME}")
print(f"Region: {TEST_REGION}")
print()
print("Conditions that triggered the alert:")
for cond in TEST_CONDITIONS_MET:
    print(f"  - {cond['indicator']}: {cond['actual_value']} {cond['operator']} {cond['threshold_value']} ✓")
print()
print("Sending email...")
print()

# Send the test email
result = send_drought_alert(
    user_email=TEST_EMAIL,
    user_name=TEST_USER_NAME,
    trigger_name=TEST_TRIGGER_NAME,
    trigger_id=TEST_TRIGGER_ID,
    user_id=TEST_USER_ID,
    region=TEST_REGION,
    conditions_met=TEST_CONDITIONS_MET,
    recommendations=TEST_RECOMMENDATIONS
)

# Print results
print("=" * 80)
print("RESULTS")
print("=" * 80)
print()

if result.get("success"):
    print("✅ SUCCESS! Email sent successfully")
    print()
    print("Details:")
    print(f"  - Message ID: {result.get('message_id', 'N/A')}")
    print(f"  - Recipient: {TEST_EMAIL}")
    print(f"  - Status: {result.get('message', 'Sent')}")
    print()
    print("📧 Check your inbox at regan@axiomintelligence.co.nz")
    print("   (Check spam folder if you don't see it)")
else:
    print("❌ FAILED to send email")
    print()
    print(f"Error: {result.get('message', 'Unknown error')}")
    print()
    if "SENDGRID_API_KEY not configured" in result.get("message", ""):
        print("💡 Make sure SENDGRID_API_KEY is set in backend/.env")

print()
print("=" * 80)
