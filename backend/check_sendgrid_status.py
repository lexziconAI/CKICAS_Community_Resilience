"""
Check SendGrid Activity - See if emails were actually delivered
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("SENDGRID STATUS CHECK")
print("=" * 80)
print()
print("1. Emails show Status 202 (Accepted) - this means SendGrid accepted them")
print("   but does NOT guarantee delivery to inbox.")
print()
print("2. NEXT STEPS TO CHECK:")
print()
print("   A. CHECK SPAM FOLDER")
print("      - Open Gmail: https://mail.google.com/mail/u/0/#spam")
print("      - Search for: from:reganduffnz@gmail.com")
print("      - Look for emails with subject 'Drought Alert' or 'SendGrid Test'")
print()
print("   B. CHECK SENDGRID ACTIVITY FEED")
print("      - Go to: https://app.sendgrid.com/email_activity")
print("      - Filter by: to email = reganduffnz@gmail.com")
print("      - Look for recent emails (last 10 minutes)")
print("      - Check if they show 'Delivered', 'Bounced', or 'Dropped'")
print()
print("   C. COMMON ISSUES:")
print("      - Gmail filtering: Emails from your own address might be filtered")
print("      - Sender verification: Even if verified, Gmail may not trust SendGrid")
print("      - Delay: Can take 1-5 minutes for delivery")
print()
print("3. ALTERNATIVE TEST:")
print("   Try sending to a DIFFERENT email (not Gmail) like:")
print("   - Outlook/Hotmail")
print("   - Your work email (regan@axiomintelligence.co.nz)")
print()
print("=" * 80)
print()

# Show current config
SENDGRID_FROM = os.getenv("SENDGRID_FROM_EMAIL", "")
print(f"Current sender email: {SENDGRID_FROM}")
print(f"Current recipient: reganduffnz@gmail.com")
print()
print("RECOMMENDATION:")
print("Since sender and recipient are the same (both Gmail), Gmail might be")
print("filtering or blocking these. Try sending to regan@axiomintelligence.co.nz")
print("or another non-Gmail address instead.")
print()
print("=" * 80)
