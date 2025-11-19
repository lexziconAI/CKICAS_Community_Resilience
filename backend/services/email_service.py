"""
CKCIAS Drought Monitor - Email Notification Service
SendGrid email service for sending drought alert notifications
Day 3 MVP - Beautiful HTML emails with actionable recommendations
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logging.warning("SendGrid library not installed. Install with: pip install sendgrid")

from database import get_db_connection, log_notification
from config import SENDGRID_API_KEY, AVAILABLE_INDICATORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email configuration
SENDER_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "drought-alerts@ckcias.nz")
SENDER_NAME = os.getenv("SENDGRID_FROM_NAME", "CKCIAS Drought Monitor")
RATE_LIMIT_HOURS = 6  # Don't send duplicate alerts within 6 hours


def get_email_template() -> str:
    """
    Returns the HTML email template for drought alerts.
    Uses inline CSS for maximum email client compatibility.
    CKCIAS color scheme: blues (#1E40AF, #3B82F6) and greens (#059669, #10B981)
    """
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CKCIAS Drought Alert</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f3f4f6;">
        <tr>
            <td style="padding: 20px 0;">
                <!-- Main Container -->
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">
                                🌡️ CKCIAS Drought Alert
                            </h1>
                            <p style="margin: 10px 0 0 0; color: #E0E7FF; font-size: 14px;">
                                Climate Knowledge for Community Impact Assessment
                            </p>
                        </td>
                    </tr>

                    <!-- Greeting -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px;">
                            <p style="margin: 0; font-size: 16px; color: #1F2937; line-height: 1.6;">
                                Hello <strong>{{USER_NAME}}</strong>,
                            </p>
                            <p style="margin: 15px 0 0 0; font-size: 16px; color: #1F2937; line-height: 1.6;">
                                Your drought monitoring trigger <strong>"{{TRIGGER_NAME}}"</strong> has been activated for <strong>{{REGION}}</strong>.
                            </p>
                        </td>
                    </tr>

                    <!-- Alert Summary Box -->
                    <tr>
                        <td style="padding: 0 30px 20px 30px;">
                            <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; border-radius: 4px;">
                                <p style="margin: 0; font-size: 14px; color: #92400E; line-height: 1.6;">
                                    <strong>⚠️ Alert Status:</strong> The following conditions have been met and require your attention.
                                </p>
                            </div>
                        </td>
                    </tr>

                    <!-- Conditions Table -->
                    <tr>
                        <td style="padding: 0 30px 20px 30px;">
                            <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #1F2937; border-bottom: 2px solid #3B82F6; padding-bottom: 8px;">
                                Conditions Met
                            </h2>
                            {{CONDITIONS_TABLE}}
                        </td>
                    </tr>

                    <!-- Recommendations -->
                    <tr>
                        <td style="padding: 0 30px 20px 30px;">
                            <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #1F2937; border-bottom: 2px solid #059669; padding-bottom: 8px;">
                                Recommended Actions
                            </h2>
                            {{RECOMMENDATIONS}}
                        </td>
                    </tr>

                    <!-- Call to Action -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px; text-align: center;">
                            <p style="margin: 0 0 20px 0; font-size: 14px; color: #6B7280; line-height: 1.6;">
                                Monitor conditions closely and take appropriate action based on your organization's drought response plan.
                            </p>
                            <a href="https://ckcias.nz/dashboard" style="display: inline-block; background-color: #3B82F6; color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 6px; font-weight: bold; font-size: 16px;">
                                View Dashboard
                            </a>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #F9FAFB; padding: 20px 30px; border-radius: 0 0 8px 8px; border-top: 1px solid #E5E7EB;">
                            <p style="margin: 0 0 10px 0; font-size: 12px; color: #6B7280; line-height: 1.6; text-align: center;">
                                <strong>CKCIAS Drought Monitor</strong><br>
                                Climate Knowledge for Community Impact Assessment<br>
                                Supporting New Zealand communities with climate resilience
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 11px; color: #9CA3AF; line-height: 1.6; text-align: center;">
                                This is an automated alert from your drought monitoring system.<br>
                                Alert sent: {{TIMESTAMP}}<br>
                                Questions? Contact: <a href="mailto:support@ckcias.nz" style="color: #3B82F6; text-decoration: none;">support@ckcias.nz</a>
                            </p>
                            <p style="margin: 15px 0 0 0; font-size: 10px; color: #9CA3AF; text-align: center;">
                                <a href="https://ckcias.nz/unsubscribe" style="color: #9CA3AF; text-decoration: underline;">Unsubscribe</a> |
                                <a href="https://ckcias.nz/settings" style="color: #9CA3AF; text-decoration: underline;">Manage Alerts</a>
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def format_conditions_table(conditions_met: List[Dict[str, Any]]) -> str:
    """
    Formats the conditions that were met as an HTML table.

    Args:
        conditions_met: List of conditions with indicator, operator, threshold, and actual value

    Returns:
        HTML table string

    Example condition:
        {
            "indicator": "temp",
            "operator": ">",
            "threshold": 25.0,
            "actual_value": 28.5
        }
    """
    if not conditions_met:
        return '<p style="color: #6B7280; font-size: 14px;">No conditions specified.</p>'

    # Start table
    html = """
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #F9FAFB; border-radius: 6px; overflow: hidden;">
        <thead>
            <tr style="background-color: #3B82F6; color: #ffffff;">
                <th style="padding: 12px; text-align: left; font-size: 14px; font-weight: 600;">Indicator</th>
                <th style="padding: 12px; text-align: center; font-size: 14px; font-weight: 600;">Condition</th>
                <th style="padding: 12px; text-align: center; font-size: 14px; font-weight: 600;">Threshold</th>
                <th style="padding: 12px; text-align: center; font-size: 14px; font-weight: 600;">Actual Value</th>
                <th style="padding: 12px; text-align: center; font-size: 14px; font-weight: 600;">Status</th>
            </tr>
        </thead>
        <tbody>
    """

    # Add each condition row
    for i, condition in enumerate(conditions_met):
        indicator = condition.get("indicator", "unknown")
        operator = condition.get("operator", "")
        threshold = condition.get("threshold", 0)
        actual_value = condition.get("actual_value", 0)

        # Get indicator metadata
        indicator_info = AVAILABLE_INDICATORS.get(indicator, {
            "label": indicator.capitalize(),
            "unit": ""
        })

        label = indicator_info["label"]
        unit = indicator_info["unit"]

        # Determine if condition is met (for status icon)
        is_met = evaluate_condition(actual_value, operator, threshold)
        status_icon = "✅" if is_met else "❌"
        status_color = "#059669" if is_met else "#DC2626"

        # Alternate row colors
        bg_color = "#FFFFFF" if i % 2 == 0 else "#F9FAFB"

        html += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 12px; font-size: 14px; color: #1F2937; border-bottom: 1px solid #E5E7EB;">
                    <strong>{label}</strong>
                </td>
                <td style="padding: 12px; text-align: center; font-size: 14px; color: #1F2937; border-bottom: 1px solid #E5E7EB;">
                    {operator}
                </td>
                <td style="padding: 12px; text-align: center; font-size: 14px; color: #1F2937; border-bottom: 1px solid #E5E7EB;">
                    {threshold} {unit}
                </td>
                <td style="padding: 12px; text-align: center; font-size: 14px; font-weight: 600; color: {status_color}; border-bottom: 1px solid #E5E7EB;">
                    {actual_value} {unit}
                </td>
                <td style="padding: 12px; text-align: center; font-size: 18px; border-bottom: 1px solid #E5E7EB;">
                    {status_icon}
                </td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    """

    return html


def evaluate_condition(actual_value: float, operator: str, threshold: float) -> bool:
    """
    Evaluates if a condition is met.

    Args:
        actual_value: The actual measured value
        operator: Comparison operator (>, <, >=, <=, ==)
        threshold: The threshold value to compare against

    Returns:
        True if condition is met, False otherwise
    """
    if operator == ">":
        return actual_value > threshold
    elif operator == "<":
        return actual_value < threshold
    elif operator == ">=":
        return actual_value >= threshold
    elif operator == "<=":
        return actual_value <= threshold
    elif operator == "==":
        return actual_value == threshold
    return False


def get_recommendations_html(conditions_met: List[Dict[str, Any]]) -> str:
    """
    Generates HTML list of recommendations based on which conditions triggered.

    Args:
        conditions_met: List of conditions that were met

    Returns:
        HTML unordered list of recommendations
    """
    recommendations = []

    # Check which indicators triggered
    triggered_indicators = {c.get("indicator") for c in conditions_met}

    # Temperature-based recommendations
    if "temp" in triggered_indicators:
        recommendations.append({
            "icon": "🌡️",
            "title": "High Temperature Alert",
            "text": "Monitor livestock for heat stress. Ensure adequate shade and water supply. Consider adjusting grazing schedules to cooler hours."
        })

    # Rainfall-based recommendations
    if "rainfall" in triggered_indicators:
        recommendations.append({
            "icon": "💧",
            "title": "Low Rainfall Alert",
            "text": "Implement water conservation measures. Review irrigation schedules and prioritize critical crops. Check water storage levels."
        })

    # Humidity-based recommendations
    if "humidity" in triggered_indicators:
        recommendations.append({
            "icon": "💨",
            "title": "Low Humidity Alert",
            "text": "Increase monitoring for fire risk. Consider moisture retention strategies for crops. Review drying infrastructure capacity."
        })

    # Wind speed-based recommendations
    if "wind_speed" in triggered_indicators:
        recommendations.append({
            "icon": "🌬️",
            "title": "High Wind Speed Alert",
            "text": "Secure loose materials and equipment. Monitor for wind damage to crops and structures. Delay spray operations if planned."
        })

    # General drought recommendations
    recommendations.append({
        "icon": "📋",
        "title": "General Drought Response",
        "text": "Activate your drought response plan. Communicate with your team about water restrictions. Monitor local authority drought status updates."
    })

    recommendations.append({
        "icon": "📞",
        "title": "Seek Expert Advice",
        "text": "Contact your local agricultural advisor or DairyNZ consulting officer for region-specific guidance and support."
    })

    # Build HTML
    html = '<div style="background-color: #F0FDF4; border-radius: 6px; padding: 15px;">'

    for rec in recommendations:
        html += f"""
        <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #D1FAE5;">
            <p style="margin: 0 0 5px 0; font-size: 16px; color: #065F46;">
                <span style="font-size: 20px;">{rec['icon']}</span>
                <strong>{rec['title']}</strong>
            </p>
            <p style="margin: 0; font-size: 14px; color: #047857; line-height: 1.6;">
                {rec['text']}
            </p>
        </div>
        """

    # Remove last border
    html = html.rstrip('</div>')
    html = html[:-len('<div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #D1FAE5;">')]
    html += '<div style="margin-bottom: 15px; padding-bottom: 0px;">'
    html += """
            <p style="margin: 0 0 5px 0; font-size: 16px; color: #065F46;">
                <span style="font-size: 20px;">📞</span>
                <strong>Seek Expert Advice</strong>
            </p>
            <p style="margin: 0; font-size: 14px; color: #047857; line-height: 1.6;">
                Contact your local agricultural advisor or DairyNZ consulting officer for region-specific guidance and support.
            </p>
        </div>
    </div>
    """

    return html


def should_send_notification(trigger_id: int, user_id: int) -> bool:
    """
    Checks if a notification should be sent based on rate limiting.
    Prevents duplicate notifications within the rate limit window (default: 6 hours).

    Args:
        trigger_id: ID of the trigger
        user_id: ID of the user

    Returns:
        True if notification should be sent, False if rate limited
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get the most recent notification for this trigger and user
            cursor.execute("""
                SELECT sent_at
                FROM notification_log
                WHERE trigger_id = ? AND user_id = ?
                ORDER BY sent_at DESC
                LIMIT 1
            """, (trigger_id, user_id))

            result = cursor.fetchone()

            if not result:
                # No previous notification, OK to send
                return True

            last_sent = datetime.fromisoformat(result["sent_at"])
            time_since_last = datetime.now() - last_sent

            # Check if enough time has passed
            if time_since_last < timedelta(hours=RATE_LIMIT_HOURS):
                logger.info(
                    f"Rate limit: Last notification sent {time_since_last.total_seconds() / 3600:.1f} hours ago. "
                    f"Minimum interval: {RATE_LIMIT_HOURS} hours."
                )
                return False

            return True

    except Exception as e:
        logger.error(f"Error checking notification rate limit: {str(e)}")
        # On error, allow sending (fail open to ensure alerts get through)
        return True


def send_drought_alert(
    user_email: str,
    user_name: str,
    trigger_name: str,
    trigger_id: int,
    user_id: int,
    region: str,
    conditions_met: List[Dict[str, Any]],
    recommendations: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Sends a drought alert email to a user using SendGrid.

    Args:
        user_email: Recipient email address
        user_name: Recipient name
        trigger_name: Name of the trigger that fired
        trigger_id: ID of the trigger
        user_id: ID of the user
        region: Geographic region
        conditions_met: List of conditions that were met
        recommendations: Optional custom recommendations (uses auto-generated if None)

    Returns:
        Dictionary with status and message:
        {
            "success": True/False,
            "message": "Success/error message",
            "notification_id": ID of logged notification (if successful)
        }
    """
    try:
        # Check rate limiting
        if not should_send_notification(trigger_id, user_id):
            return {
                "success": False,
                "message": f"Rate limited: Notification already sent within {RATE_LIMIT_HOURS} hours",
                "rate_limited": True
            }

        # Check if SendGrid is available
        if not SENDGRID_AVAILABLE:
            logger.error("SendGrid library not installed")
            return {
                "success": False,
                "message": "SendGrid library not installed. Install with: pip install sendgrid"
            }

        # Check if API key is configured
        if not SENDGRID_API_KEY:
            logger.error("SendGrid API key not configured")
            return {
                "success": False,
                "message": "SENDGRID_API_KEY not configured in environment variables"
            }

        # Build the email HTML
        template = get_email_template()
        conditions_table_html = format_conditions_table(conditions_met)
        recommendations_html = get_recommendations_html(conditions_met)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S NZDT")

        # Replace template variables
        html_content = template.replace("{{USER_NAME}}", user_name)
        html_content = html_content.replace("{{TRIGGER_NAME}}", trigger_name)
        html_content = html_content.replace("{{REGION}}", region)
        html_content = html_content.replace("{{CONDITIONS_TABLE}}", conditions_table_html)
        html_content = html_content.replace("{{RECOMMENDATIONS}}", recommendations_html)
        html_content = html_content.replace("{{TIMESTAMP}}", timestamp)

        # Create plain text version (fallback)
        plain_text = f"""
CKCIAS Drought Alert

Hello {user_name},

Your drought monitoring trigger "{trigger_name}" has been activated for {region}.

ALERT STATUS: The following conditions have been met and require your attention.

CONDITIONS MET:
"""
        for condition in conditions_met:
            indicator = condition.get("indicator", "unknown")
            indicator_info = AVAILABLE_INDICATORS.get(indicator, {"label": indicator, "unit": ""})
            plain_text += f"- {indicator_info['label']}: {condition.get('actual_value')} {indicator_info['unit']} {condition.get('operator')} {condition.get('threshold')} {indicator_info['unit']}\n"

        plain_text += f"""
Please monitor conditions closely and take appropriate action.

View Dashboard: https://ckcias.nz/dashboard

---
CKCIAS Drought Monitor
This alert was sent on {timestamp}
Questions? Contact: support@ckcias.nz
"""

        # Create SendGrid message
        message = Mail(
            from_email=Email(SENDER_EMAIL, SENDER_NAME),
            to_emails=To(user_email),
            subject=f"🌡️ Drought Alert: {region} - {trigger_name}",
            plain_text_content=Content("text/plain", plain_text),
            html_content=Content("text/html", html_content)
        )

        # Send email via SendGrid
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        # Log successful send
        logger.info(f"Email sent successfully to {user_email}. Status: {response.status_code}")

        # Log to database
        conditions_dict = {
            "conditions": conditions_met,
            "region": region,
            "trigger_name": trigger_name
        }

        notification_id = log_notification(
            trigger_id=trigger_id,
            user_id=user_id,
            trigger_conditions_met=conditions_dict,
            notification_type="email"
        )

        return {
            "success": True,
            "message": f"Alert email sent successfully to {user_email}",
            "notification_id": notification_id,
            "status_code": response.status_code
        }

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {
            "success": False,
            "message": f"Error sending email: {str(e)}"
        }


def send_test_email(recipient_email: str) -> Dict[str, Any]:
    """
    Sends a test email to verify SendGrid setup.

    Args:
        recipient_email: Email address to send test to

    Returns:
        Dictionary with success status and message
    """
    logger.info(f"Sending test email to {recipient_email}")

    # Create test conditions
    test_conditions = [
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
        },
        {
            "indicator": "humidity",
            "operator": "<",
            "threshold": 60.0,
            "actual_value": 45.0
        }
    ]

    # Send using main function (with dummy IDs for testing)
    result = send_drought_alert(
        user_email=recipient_email,
        user_name="Test User",
        trigger_name="Test Drought Alert",
        trigger_id=999,  # Test trigger ID
        user_id=999,     # Test user ID
        region="Test Region",
        conditions_met=test_conditions
    )

    return result


def get_sendgrid_setup_instructions() -> str:
    """
    Returns instructions for setting up SendGrid API key.

    Returns:
        Formatted string with setup instructions
    """
    return """
╔══════════════════════════════════════════════════════════════════════════╗
║                    SENDGRID API KEY SETUP INSTRUCTIONS                   ║
╚══════════════════════════════════════════════════════════════════════════╝

1. CREATE SENDGRID ACCOUNT (FREE TIER)
   ────────────────────────────────────
   • Go to: https://signup.sendgrid.com/
   • Sign up for free account (100 emails/day)
   • Verify your email address

2. CREATE API KEY
   ────────────────
   • Log in to SendGrid dashboard
   • Navigate to: Settings > API Keys
   • Click "Create API Key"
   • Name: "CKCIAS Drought Monitor"
   • Permissions: "Full Access" (or "Mail Send" only)
   • Click "Create & View"
   • COPY THE API KEY (you won't see it again!)

3. CONFIGURE ENVIRONMENT VARIABLE
   ────────────────────────────────
   • Add to your .env file:

     SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

   • Or export in your shell:

     export SENDGRID_API_KEY="SG.xxxxx..."

4. VERIFY SENDER IDENTITY (REQUIRED FOR FREE TIER)
   ─────────────────────────────────────────────────
   • Go to: Settings > Sender Authentication
   • Choose "Verify a Single Sender"
   • Enter your email address (e.g., regan@axiomintelligence.co.nz)
   • Check email and click verification link
   • Update SENDER_EMAIL in email_service.py to match verified email

5. TEST YOUR SETUP
   ───────────────
   • Run the test function:

     python -c "from services.email_service import send_test_email; \\
                print(send_test_email('your-email@example.com'))"

6. FREE TIER LIMITS
   ────────────────
   • 100 emails per day
   • Rate limiting: 6 hours between duplicate alerts
   • Perfect for MVP and testing!

╔══════════════════════════════════════════════════════════════════════════╗
║  Need help? Contact: regan@axiomintelligence.co.nz                       ║
╚══════════════════════════════════════════════════════════════════════════╝
"""


if __name__ == "__main__":
    """
    Test the email service when run directly.
    """
    print(get_sendgrid_setup_instructions())

    # Check if SendGrid is configured
    if SENDGRID_API_KEY:
        print("\n✅ SendGrid API key found in environment")
        print(f"   Key preview: {SENDGRID_API_KEY[:10]}...{SENDGRID_API_KEY[-5:]}")

        # Prompt for test email
        test_email = input("\nEnter email address to send test alert (or press Enter to skip): ").strip()
        if test_email:
            print(f"\n📧 Sending test email to {test_email}...")
            result = send_test_email(test_email)

            if result["success"]:
                print(f"✅ {result['message']}")
                print(f"   Status code: {result.get('status_code', 'N/A')}")
            else:
                print(f"❌ {result['message']}")
    else:
        print("\n⚠️  SendGrid API key NOT found in environment")
        print("   Please follow the setup instructions above.")
