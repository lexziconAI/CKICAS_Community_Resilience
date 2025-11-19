"""
Example script demonstrating how to use the trigger evaluation endpoint

This script shows how to call the /api/triggers/evaluate endpoint
to evaluate drought triggers against weather data.

Prerequisites:
- Backend server must be running (python3 main.py)
- Database must be initialized with users and triggers
"""

import requests
import json


def test_evaluation_endpoint():
    """Test the trigger evaluation endpoint"""

    # API endpoint
    BASE_URL = "http://localhost:9100"
    EVALUATE_ENDPOINT = f"{BASE_URL}/api/triggers/evaluate"

    print("="*70)
    print("TESTING TRIGGER EVALUATION ENDPOINT")
    print("="*70)

    # Test data - Weather conditions that should trigger Tim's alert
    # Tim's trigger: any_2 of (temp>25, rainfall<2, humidity<60)
    test_payload = {
        "user_id": 2,  # Tim House
        "weather_data": {
            "temperature": 27.5,  # > 25 ✓
            "rainfall": 1.2,      # < 2 ✓
            "humidity": 65.0,     # NOT < 60 ✗
            "wind_speed": 15.0
        }
    }

    print("\nRequest payload:")
    print(json.dumps(test_payload, indent=2))

    try:
        # Make POST request
        print(f"\nSending POST request to {EVALUATE_ENDPOINT}...")
        response = requests.post(EVALUATE_ENDPOINT, json=test_payload)

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print("\n" + "="*70)
            print("EVALUATION RESULTS")
            print("="*70)

            print(f"\nUser ID: {result['user_id']}")
            print(f"Total alerts triggered: {result['total_alerts']}")
            print(f"Evaluated at: {result['evaluated_at']}")

            if result['total_alerts'] > 0:
                print("\n" + "-"*70)
                print("TRIGGERED ALERTS")
                print("-"*70)

                for i, alert in enumerate(result['alerts'], 1):
                    trigger = alert['trigger']
                    conditions = alert['conditions_met']
                    recommendations = alert['recommendations']

                    print(f"\nALERT #{i}")
                    print(f"  Trigger Name: {trigger['name']}")
                    print(f"  Region: {trigger['region']}")
                    print(f"  Combination Rule: {trigger['combination_rule']}")
                    print(f"  Active: {trigger['is_active']}")

                    print(f"\n  Conditions ({sum(1 for c in conditions if c['met'])}/{len(conditions)} met):")
                    for condition in conditions:
                        met_icon = "✓" if condition['met'] else "✗"
                        print(f"    {met_icon} {condition['indicator']} "
                              f"{condition['operator']} {condition['threshold_value']} "
                              f"(actual: {condition['actual_value']})")

                    print(f"\n  Recommendations ({len(recommendations)}):")
                    for j, rec in enumerate(recommendations, 1):
                        print(f"    {j}. {rec}")

                print("\n" + "="*70)
                print("✓ SUCCESS: Trigger evaluation completed successfully")
                print("="*70)

            else:
                print("\n✓ No alerts triggered (all conditions within normal range)")

        else:
            print(f"\n✗ ERROR: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend server")
        print("Make sure the backend server is running:")
        print("  cd backend")
        print("  python3 main.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")


def test_no_trigger_scenario():
    """Test scenario where no triggers should fire"""

    BASE_URL = "http://localhost:9100"
    EVALUATE_ENDPOINT = f"{BASE_URL}/api/triggers/evaluate"

    print("\n\n" + "="*70)
    print("TESTING NO-TRIGGER SCENARIO")
    print("="*70)

    # Weather data with normal conditions
    test_payload = {
        "user_id": 2,  # Tim House
        "weather_data": {
            "temperature": 20.0,  # NOT > 25 ✗
            "rainfall": 5.0,      # NOT < 2 ✗
            "humidity": 70.0,     # NOT < 60 ✗
            "wind_speed": 10.0
        }
    }

    print("\nRequest payload:")
    print(json.dumps(test_payload, indent=2))

    try:
        print(f"\nSending POST request to {EVALUATE_ENDPOINT}...")
        response = requests.post(EVALUATE_ENDPOINT, json=test_payload)

        if response.status_code == 200:
            result = response.json()

            print(f"\nTotal alerts triggered: {result['total_alerts']}")

            if result['total_alerts'] == 0:
                print("✓ SUCCESS: No alerts triggered (as expected)")
            else:
                print(f"✗ UNEXPECTED: Expected 0 alerts but got {result['total_alerts']}")

        else:
            print(f"✗ ERROR: Request failed with status {response.status_code}")

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")


if __name__ == "__main__":
    # Test 1: Triggering scenario
    test_evaluation_endpoint()

    # Test 2: Non-triggering scenario
    test_no_trigger_scenario()

    print("\n\n" + "="*70)
    print("ENDPOINT TESTING COMPLETE")
    print("="*70)
    print("\nTo use this endpoint in your application:")
    print("\n  import requests")
    print("  ")
    print("  response = requests.post('http://localhost:9100/api/triggers/evaluate', json={")
    print("      'user_id': 2,")
    print("      'weather_data': {")
    print("          'temperature': 27.5,")
    print("          'rainfall': 1.2,")
    print("          'humidity': 55.0,")
    print("          'wind_speed': 15.0")
    print("      }")
    print("  })")
    print("  ")
    print("  alerts = response.json()['alerts']")
    print("  for alert in alerts:")
    print("      print(f\"ALERT: {alert['trigger']['name']}\")")
    print("="*70)
