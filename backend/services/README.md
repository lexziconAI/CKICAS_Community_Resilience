# CKCIAS Drought Monitor - Email Service

SendGrid-powered email notification service for drought alerts (Day 3 MVP).

## Overview

When drought conditions trigger alerts, this service sends beautiful, actionable email notifications to users with:
- Professional HTML email design with CKCIAS branding
- Detailed conditions table showing what triggered the alert
- Actionable recommendations based on the specific conditions
- Rate limiting to prevent notification spam (6-hour minimum between duplicate alerts)
- Complete audit trail in the database

## Features

### 1. SendGrid Integration
- Uses SendGrid free tier (100 emails/day)
- Reads `SENDGRID_API_KEY` from environment variables
- Graceful degradation if SendGrid is unavailable
- Comprehensive error handling and logging

### 2. Beautiful HTML Email Templates
- **Responsive design**: Mobile-friendly layout
- **CKCIAS branding**: Professional color scheme (blues #1E40AF, #3B82F6 and greens #059669, #10B981)
- **Inline CSS**: Maximum compatibility with email clients (Gmail, Outlook, etc.)
- **Plain text fallback**: For email clients that don't support HTML

### 3. Core Functions

#### `send_drought_alert()`
Main function to send drought alert emails.

```python
from services.email_service import send_drought_alert

result = send_drought_alert(
    user_email="tim.house@fonterra.com",
    user_name="Tim House",
    trigger_name="Taranaki Drought Alert",
    trigger_id=1,
    user_id=2,
    region="Taranaki",
    conditions_met=[
        {
            "indicator": "temp",
            "operator": ">",
            "threshold": 25.0,
            "actual_value": 28.5
        },
        {
            "indicator": "rainfall",
            "operator": "<",
            "threshold": 2.0,
            "actual_value": 0.8
        }
    ]
)

if result["success"]:
    print(f"Email sent! Notification ID: {result['notification_id']}")
else:
    print(f"Failed: {result['message']}")
```

#### `should_send_notification()`
Checks rate limiting to prevent spam.

```python
from services.email_service import should_send_notification

if should_send_notification(trigger_id=1, user_id=2):
    # OK to send
    send_drought_alert(...)
else:
    # Rate limited - too soon since last alert
    print("Skipping: Already sent notification within 6 hours")
```

#### `format_conditions_table()`
Formats conditions as HTML table for email display.

#### `get_recommendations_html()`
Generates smart recommendations based on which indicators triggered.

#### `send_test_email()`
Sends a test email to verify setup.

```python
from services.email_service import send_test_email

result = send_test_email("your-email@example.com")
print(result)
```

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs `sendgrid>=6.11.0` along with other dependencies.

### 2. Set Up SendGrid API Key

See detailed instructions below in **SendGrid Setup**.

### 3. Verify Installation

```bash
python -c "from services.email_service import get_sendgrid_setup_instructions; print(get_sendgrid_setup_instructions())"
```

## SendGrid Setup

### Step 1: Create SendGrid Account (FREE)

1. Go to https://signup.sendgrid.com/
2. Sign up for free account (100 emails/day - perfect for MVP!)
3. Verify your email address

### Step 2: Create API Key

1. Log in to SendGrid dashboard
2. Navigate to: **Settings > API Keys**
3. Click **"Create API Key"**
4. Name: `CKCIAS Drought Monitor`
5. Permissions: **Full Access** (or **Mail Send** only for security)
6. Click **"Create & View"**
7. **COPY THE API KEY** - you won't see it again!

### Step 3: Configure Environment Variable

Add to your `.env` file in `/backend`:

```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Or export in your shell:

```bash
export SENDGRID_API_KEY="SG.xxxxx..."
```

### Step 4: Verify Sender Identity (REQUIRED for Free Tier)

SendGrid free tier requires sender verification:

1. Go to: **Settings > Sender Authentication**
2. Choose **"Verify a Single Sender"**
3. Enter your email address (e.g., `regan@axiomintelligence.co.nz`)
4. Check your email and click verification link
5. Update `SENDER_EMAIL` in `email_service.py` to match your verified email:

```python
SENDER_EMAIL = "regan@axiomintelligence.co.nz"  # Change to your verified email
```

### Step 5: Test Your Setup

```bash
cd backend
python3 -c "from services.email_service import send_test_email; print(send_test_email('your-email@example.com'))"
```

You should receive a beautiful test email!

## Email Template Design

### Header
- CKCIAS gradient header (blue gradient)
- Clear title with emoji: "🌡️ CKCIAS Drought Alert"

### Alert Summary
- Yellow warning box with alert status
- Clear indication that conditions require attention

### Conditions Table
- Professional table layout
- Shows: Indicator | Condition | Threshold | Actual Value | Status
- Color-coded values (green ✅ for met conditions, red ❌ for unmet)
- Alternating row colors for readability

### Recommendations Section
- Icon-based recommendations
- Specific to the indicators that triggered
- Actionable advice (not just warnings)
- Examples:
  - 🌡️ High Temperature: Monitor livestock for heat stress
  - 💧 Low Rainfall: Implement water conservation measures
  - 💨 Low Humidity: Increase fire risk monitoring
  - 📋 General drought response activation
  - 📞 Contact local agricultural advisors

### Call to Action
- Blue button: "View Dashboard"
- Links to dashboard for more details

### Footer
- CKCIAS branding and mission
- Timestamp of alert
- Contact information
- Unsubscribe link (placeholder for future)

## Rate Limiting

The service implements smart rate limiting to prevent notification spam:

- **Default**: 6 hours minimum between duplicate alerts
- **Database-tracked**: Uses `notification_log` table
- **Per-trigger, per-user**: Different triggers can send independently
- **Fail-open**: If database check fails, allows sending (ensures critical alerts get through)

Configure rate limit in `email_service.py`:

```python
RATE_LIMIT_HOURS = 6  # Change to your preference
```

## Database Integration

All email notifications are logged to the `notification_log` table:

```sql
CREATE TABLE notification_log (
    id INTEGER PRIMARY KEY,
    trigger_id INTEGER,
    user_id INTEGER,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notification_type TEXT DEFAULT 'email',
    trigger_conditions_met TEXT  -- JSON of conditions
);
```

This provides:
- Complete audit trail
- Rate limiting data
- Analytics on alert frequency
- User notification history

## Error Handling

The service handles multiple error scenarios gracefully:

1. **SendGrid library not installed**: Returns error message with installation instructions
2. **API key missing**: Returns error message with setup instructions
3. **SendGrid API failure**: Catches and logs exception, returns detailed error
4. **Database errors**: Logs error but doesn't block email sending
5. **Rate limiting**: Returns clear message about when next notification can be sent

All errors are logged using Python's `logging` module.

## Testing

### Generate Email Preview (No SendGrid Required)

```bash
cd backend/services
python3 email_preview.py
```

This creates `email_preview.html` that you can open in your browser to see the email design without sending anything.

### Send Test Email

```bash
cd backend
python3 -c "from services.email_service import send_test_email; print(send_test_email('your-email@example.com'))"
```

### View Setup Instructions

```bash
cd backend
python3 services/email_service.py
```

## Email Content Examples

### Subject Line
```
🌡️ Drought Alert: Taranaki - Taranaki Drought Alert
```

### Sample Conditions Table
| Indicator | Condition | Threshold | Actual Value | Status |
|-----------|-----------|-----------|--------------|--------|
| Temperature | > | 25 °C | 28.5 °C | ✅ |
| Rainfall | < | 2 mm | 0.8 mm | ✅ |
| Humidity | < | 60 % | 45 % | ✅ |

### Sample Recommendations
- 🌡️ **High Temperature Alert**: Monitor livestock for heat stress. Ensure adequate shade and water supply.
- 💧 **Low Rainfall Alert**: Implement water conservation measures. Review irrigation schedules.
- 💨 **Low Humidity Alert**: Increase monitoring for fire risk. Consider moisture retention strategies.
- 📋 **General Drought Response**: Activate your drought response plan. Communicate with your team.
- 📞 **Seek Expert Advice**: Contact your local agricultural advisor or DairyNZ consulting officer.

## Integration with Drought Monitor

To integrate with the main drought monitoring system:

```python
from services.email_service import send_drought_alert, should_send_notification
from database import get_user_by_email

# When a trigger fires
user = get_user_by_email("tim.house@fonterra.com")

# Check rate limiting
if should_send_notification(trigger_id=1, user_id=user["id"]):
    # Send the alert
    result = send_drought_alert(
        user_email=user["email"],
        user_name=user["name"],
        trigger_name="Taranaki Drought Alert",
        trigger_id=1,
        user_id=user["id"],
        region=user["region"],
        conditions_met=[...]  # From trigger evaluation
    )

    if result["success"]:
        print(f"✅ Alert sent to {user['name']}")
    else:
        print(f"❌ Failed: {result['message']}")
else:
    print("⏭️ Skipped: Rate limited")
```

## Free Tier Limits

SendGrid free tier provides:
- ✅ 100 emails per day
- ✅ No credit card required
- ✅ Perfect for MVP and testing
- ✅ Single sender verification

With rate limiting (6 hours), this supports:
- Up to 4 alerts per day per user
- ~25 active users receiving 4 alerts/day
- Plenty for MVP phase!

## Troubleshooting

### "SendGrid library not installed"
```bash
pip install sendgrid
```

### "SENDGRID_API_KEY not configured"
Add to `.env`:
```
SENDGRID_API_KEY=SG.your_key_here
```

### "Sender identity not verified"
1. Go to SendGrid dashboard
2. Settings > Sender Authentication
3. Verify a Single Sender
4. Use verified email in `SENDER_EMAIL`

### Emails not arriving
1. Check spam folder
2. Verify sender email is verified in SendGrid
3. Check SendGrid dashboard for delivery status
4. Review SendGrid activity feed for errors

### Rate limited
Wait 6 hours, or manually delete entry from `notification_log` table for testing:
```sql
DELETE FROM notification_log WHERE trigger_id = 1 AND user_id = 2;
```

## Future Enhancements

Potential improvements for post-MVP:

- [ ] SMS notifications via Twilio
- [ ] Push notifications
- [ ] Email preferences (frequency, types)
- [ ] Unsubscribe functionality
- [ ] Email template customization per user
- [ ] A/B testing of recommendations
- [ ] Analytics dashboard for notification effectiveness
- [ ] Multi-language support
- [ ] Batch sending for multiple users
- [ ] Priority levels for alerts

## Support

Questions or issues?
- Email: regan@axiomintelligence.co.nz
- GitHub: [Repository link]
- SendGrid Support: https://support.sendgrid.com/

---

**Built for CKCIAS Drought Monitor MVP (Day 3)**
Climate Knowledge for Community Impact Assessment
Supporting New Zealand communities with climate resilience
