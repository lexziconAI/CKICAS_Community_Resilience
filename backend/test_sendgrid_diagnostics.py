"""
SendGrid Diagnostic Test
Checks API key, sender verification, and provides detailed error information
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDER_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "")

print("=" * 80)
print("SENDGRID DIAGNOSTIC TEST")
print("=" * 80)
print()

# Check 1: API Key
print("1. Checking API Key Configuration...")
if not SENDGRID_API_KEY:
    print("   ❌ SENDGRID_API_KEY is not set in .env")
    sys.exit(1)
else:
    print(f"   ✓ API key found: {SENDGRID_API_KEY[:15]}...")
print()

# Check 2: Sender Email
print("2. Checking Sender Email Configuration...")
if not SENDER_EMAIL:
    print("   ❌ SENDGRID_FROM_EMAIL is not set in .env")
    sys.exit(1)
else:
    print(f"   ✓ Sender email: {SENDER_EMAIL}")
print()

# Check 3: Try to import SendGrid
print("3. Checking SendGrid library...")
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    print("   ✓ SendGrid library imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import SendGrid: {e}")
    sys.exit(1)
print()

# Check 4: Test API connection with detailed error
print("4. Testing SendGrid API Connection...")
try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    print("   ✓ SendGrid client created")

    # Try to send a simple test email
    message = Mail(
        from_email=Email(SENDER_EMAIL, "CKCIAS Test"),
        to_emails=To(SENDER_EMAIL),  # Send to self
        subject="SendGrid Test",
        plain_text_content=Content("text/plain", "This is a test email from CKCIAS")
    )

    print(f"   → Attempting to send test email from {SENDER_EMAIL} to {SENDER_EMAIL}...")
    response = sg.send(message)

    print()
    print("=" * 80)
    print("✅ SUCCESS! Email sent successfully")
    print("=" * 80)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.body}")
    print(f"Response Headers: {response.headers}")
    print()

except Exception as e:
    print()
    print("=" * 80)
    print("❌ FAILED - Detailed Error Information")
    print("=" * 80)
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print()

    # Try to get more details from the error
    if hasattr(e, 'body'):
        print(f"Error Body: {e.body}")
    if hasattr(e, 'status_code'):
        print(f"Status Code: {e.status_code}")
    if hasattr(e, 'reason'):
        print(f"Reason: {e.reason}")
    if hasattr(e, 'headers'):
        print(f"Headers: {e.headers}")

    print()
    print("=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    print()

    if "403" in str(e) or "Forbidden" in str(e):
        print("❌ HTTP 403 Forbidden Error")
        print()
        print("This error means the sender email is NOT verified in SendGrid.")
        print()
        print("To fix this:")
        print(f"1. Go to: https://app.sendgrid.com/settings/sender_auth/senders")
        print(f"2. Find the sender: {SENDER_EMAIL}")
        print(f"3. Check if it shows a green 'Verified' badge")
        print(f"4. If not verified:")
        print(f"   - Check your email inbox at {SENDER_EMAIL}")
        print(f"   - Look for an email from SendGrid with subject 'Sender Verification'")
        print(f"   - Click the verification link in that email")
        print(f"5. If no verification email:")
        print(f"   - Click 'Resend Verification' in the SendGrid dashboard")
        print(f"   - Check spam folder")
        print()
    elif "401" in str(e) or "Unauthorized" in str(e):
        print("❌ HTTP 401 Unauthorized Error")
        print()
        print("This error means the API key is invalid or doesn't have permission.")
        print()
        print("To fix this:")
        print("1. Go to: https://app.sendgrid.com/settings/api_keys")
        print("2. Create a NEW API key with 'Full Access' or 'Mail Send' permission")
        print("3. Copy the new key and update backend/.env")
        print()
    else:
        print(f"Unknown error. Please check SendGrid dashboard for more details.")
        print()

    print("=" * 80)
    sys.exit(1)

print("All checks passed!")
print("=" * 80)
