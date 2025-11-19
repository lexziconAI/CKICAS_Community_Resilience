"""
Example Usage: CKCIAS Email Service Integration
Demonstrates how to integrate email notifications with the drought monitor
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from email_service import send_drought_alert, should_send_notification, send_test_email
from database import get_user_by_email, get_user_triggers, get_trigger_conditions


def example_1_simple_test():
    """
    Example 1: Send a simple test email
    This is the quickest way to verify your SendGrid setup.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Send a test email")
    print("="*70)

    # Replace with your email
    test_email = "regan@axiomintelligence.co.nz"

    result = send_test_email(test_email)

    if result["success"]:
        print(f"✅ Success! Test email sent to {test_email}")
        print(f"   Check your inbox (and spam folder)")
    else:
        print(f"❌ Failed: {result['message']}")


def example_2_send_real_alert():
    """
    Example 2: Send a real drought alert to Tim House
    Uses actual user and trigger data from the database.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Send real drought alert")
    print("="*70)

    # Get Tim House from database
    user = get_user_by_email("tim.house@fonterra.com")

    if not user:
        print("❌ User not found. Run database.py to seed users first.")
        return

    print(f"📧 Recipient: {user['name']} ({user['email']})")

    # Sample conditions that triggered
    conditions_met = [
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

    # Send the alert
    result = send_drought_alert(
        user_email=user["email"],
        user_name=user["name"],
        trigger_name="Taranaki Drought Alert",
        trigger_id=1,  # Assuming trigger ID 1 exists
        user_id=user["id"],
        region=user["region"],
        conditions_met=conditions_met
    )

    if result["success"]:
        print(f"✅ Alert sent successfully!")
        print(f"   Notification ID: {result['notification_id']}")
    else:
        print(f"❌ Failed: {result['message']}")


def example_3_check_rate_limiting():
    """
    Example 3: Demonstrate rate limiting
    Shows how the system prevents duplicate alerts within 6 hours.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Check rate limiting")
    print("="*70)

    trigger_id = 1
    user_id = 2  # Tim House

    # Check if we can send
    can_send = should_send_notification(trigger_id, user_id)

    if can_send:
        print(f"✅ OK to send notification")
        print(f"   No recent notifications found for trigger {trigger_id}, user {user_id}")
    else:
        print(f"⏭️ Rate limited")
        print(f"   Notification already sent within 6 hours")
        print(f"   Trigger ID: {trigger_id}, User ID: {user_id}")


def example_4_drought_monitor_integration():
    """
    Example 4: Complete integration with drought monitor
    Shows the full workflow from trigger evaluation to email sending.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Complete drought monitor integration")
    print("="*70)

    # Get user
    user = get_user_by_email("tim.house@fonterra.com")
    if not user:
        print("❌ User not found")
        return

    # Get user's triggers
    triggers = get_user_triggers(user["id"])
    if not triggers:
        print(f"❌ No triggers found for {user['name']}")
        return

    print(f"👤 User: {user['name']}")
    print(f"📍 Region: {user['region']}")
    print(f"⚡ Triggers: {len(triggers)}")

    # Process first trigger
    trigger = triggers[0]
    print(f"\n🎯 Evaluating trigger: {trigger['name']}")

    # Get trigger conditions
    conditions = get_trigger_conditions(trigger["id"])
    print(f"   Conditions: {len(conditions)}")

    # Simulate weather data (in real app, this comes from weather API)
    current_weather = {
        "temp": 28.5,
        "rainfall": 0.8,
        "humidity": 45.0,
        "wind_speed": 15.0
    }

    # Evaluate which conditions are met
    conditions_met = []
    for condition in conditions:
        indicator = condition["indicator"]
        operator = condition["operator"]
        threshold = condition["threshold_value"]
        actual_value = current_weather.get(indicator, 0)

        # Simple condition evaluation
        is_met = False
        if operator == ">" and actual_value > threshold:
            is_met = True
        elif operator == "<" and actual_value < threshold:
            is_met = True
        elif operator == ">=" and actual_value >= threshold:
            is_met = True
        elif operator == "<=" and actual_value <= threshold:
            is_met = True
        elif operator == "==" and actual_value == threshold:
            is_met = True

        if is_met:
            conditions_met.append({
                "indicator": indicator,
                "operator": operator,
                "threshold": threshold,
                "actual_value": actual_value
            })

    print(f"   Conditions met: {len(conditions_met)}/{len(conditions)}")

    # Check combination rule
    rule = trigger["combination_rule"]
    should_trigger = False

    if rule == "any_1" and len(conditions_met) >= 1:
        should_trigger = True
    elif rule == "any_2" and len(conditions_met) >= 2:
        should_trigger = True
    elif rule == "any_3" and len(conditions_met) >= 3:
        should_trigger = True
    elif rule == "all" and len(conditions_met) == len(conditions):
        should_trigger = True

    if should_trigger:
        print(f"   🔥 TRIGGER FIRED (rule: {rule})")

        # Check rate limiting
        if should_send_notification(trigger["id"], user["id"]):
            print(f"   📧 Sending email notification...")

            # Send email
            result = send_drought_alert(
                user_email=user["email"],
                user_name=user["name"],
                trigger_name=trigger["name"],
                trigger_id=trigger["id"],
                user_id=user["id"],
                region=trigger["region"],
                conditions_met=conditions_met
            )

            if result["success"]:
                print(f"   ✅ Email sent successfully!")
                print(f"      Notification ID: {result['notification_id']}")
            else:
                print(f"   ❌ Email failed: {result['message']}")
        else:
            print(f"   ⏭️ Email skipped (rate limited)")
    else:
        print(f"   ⚪ Trigger not fired (rule: {rule}, met: {len(conditions_met)})")


def main():
    """
    Run all examples
    """
    print("\n" + "="*70)
    print("  CKCIAS EMAIL SERVICE - USAGE EXAMPLES")
    print("="*70)

    print("\nThese examples demonstrate how to integrate the email service")
    print("with the CKCIAS Drought Monitor MVP.")

    # Example 1: Simple test
    # Uncomment to send test email
    # example_1_simple_test()

    # Example 2: Send real alert
    # Uncomment to send real alert to Tim House
    # example_2_send_real_alert()

    # Example 3: Check rate limiting
    example_3_check_rate_limiting()

    # Example 4: Complete integration
    # Uncomment to run full workflow
    # example_4_drought_monitor_integration()

    print("\n" + "="*70)
    print("💡 TIP: Uncomment examples in main() to run them")
    print("="*70)


if __name__ == "__main__":
    main()
